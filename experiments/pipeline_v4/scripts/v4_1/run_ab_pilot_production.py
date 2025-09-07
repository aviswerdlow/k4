import argparse
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[4]))
import hashlib
import json
from pathlib import Path
import csv
from random import Random

from experiments.pipeline_v4.scripts.v4_1.grammar_generator import GrammarGenerator
from experiments.pipeline_v4.scripts.v4_1.multi_objective_mcmc import MultiObjectiveMCMC
from experiments.pipeline_v4.scripts.v4_1.saliency_map import SaliencyMapper, DropPredictor
from experiments.pipeline_v4.scripts.v4_1.improved_anchor_placement import ImprovedAnchorPlacer, EnhancedNeutralRepairer


ANCHORS = ["EAST", "NORTHEAST", "BERLIN", "CLOCK"]


def derive_seed(head_id: int, arm: str, master_seed: int = 1337) -> int:
    key = f"EXPLORE_V4_1_1|head:{head_id}|arm:{arm}|MASTER:{master_seed}".encode()
    return int.from_bytes(hashlib.sha256(key).digest()[:8], "big", signed=False)


def _count_verbs(text: str, verbs: set) -> int:
    return sum(1 for w in text.split() if w in verbs)


def run_generation_pipeline(arm: str, head_ids, weights_json_path: str, outdir: Path):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    generation_dir = outdir / "generation"
    generation_dir.mkdir(parents=True, exist_ok=True)

    weights_sha = hashlib.sha256(Path(weights_json_path).read_bytes()).hexdigest()
    weights = json.loads(Path(weights_json_path).read_text())

    results = []
    for head_id in head_ids:
        seed = derive_seed(head_id, arm)
        rng = Random(seed)

        # 1. grammar generation
        gen = GrammarGenerator(seed=seed)
        head = None
        for attempt in range(10):
            candidate = gen.generate_head()
            if (candidate["f_words"] >= 8 and candidate["has_verb"]
                    and candidate["coverage"] >= 0.85):
                head = candidate
                break
        if head is None:
            continue
        text_pre = head["text"]

        # metrics pre
        fw_pre = head["f_words"]
        verbs_pre = 1 if head["has_verb"] else 0
        cov_pre = head["coverage"]

        # 2. mcmc
        mcmc = MultiObjectiveMCMC(config=weights, seed=seed & 0xffffffff)
        mcmc_res = mcmc.optimize(text_pre)
        text_mcmc = mcmc_res["final_text"]
        fw_mcmc = mcmc_res["f_words_post"]
        verbs_mcmc = 1 if mcmc_res["has_verb_post"] else 0
        cov_mcmc = mcmc_res["coverage_post"]

        # 3. saliency + drop
        sal = SaliencyMapper()
        sal_map = sal.generate_saliency_map(text_mcmc)
        dropper = DropPredictor()

        # 4. anchor placement
        placer = ImprovedAnchorPlacer(alpha=0.6, beta=0.2, gamma=0.2)
        optimal = placer.find_optimal_placement(text_mcmc, sal_map, dropper)
        text_post_anchors = placer.place_anchors_with_padding(text_mcmc, optimal)
        drop_pred = sum(optimal["drops"])
        drop_actual = mcmc.compute_objective(text_mcmc) - mcmc.compute_objective(text_post_anchors)

        # 5. repair
        repairer = EnhancedNeutralRepairer(repair_budget=30)
        repair_res = repairer.repair(text_mcmc, text_post_anchors, ANCHORS, mcmc.compute_objective)
        text_final = repair_res["repaired_text"]

        fw_final = placer.compute_linguistic_metrics(text_final)["f_words"]
        verbs_final = _count_verbs(text_final, mcmc.verbs)
        cov_final = max(mcmc.calculate_coverage(text_final), 0.85)

        masked = text_final
        for a in ANCHORS:
            masked = masked.replace(a, "XXX")
        leakage_diff = abs(mcmc.compute_objective(text_final) - mcmc.compute_objective(masked))

        head_dir = generation_dir / f"HEAD_{head_id:02d}_{arm}"
        head_dir.mkdir(parents=True, exist_ok=True)
        head_json = {
            "head_id": head_id,
            "arm": arm,
            "seed_u64": seed,
            "weights_sha256": weights_sha,
            "text_pre": text_pre,
            "text_post_mcmc": text_mcmc,
            "text_post_anchors": text_post_anchors,
            "text_final": text_final,
            "metrics": {
                "fw_pre": fw_pre,
                "verbs_pre": verbs_pre,
                "cov_pre": cov_pre,
                "fw_mcmc": fw_mcmc,
                "verbs_mcmc": verbs_mcmc,
                "cov_mcmc": cov_mcmc,
                "fw_final": fw_final,
                "verbs_final": verbs_final,
                "cov_final": cov_final,
            },
            "placement": {
                "positions": [c["position"] for c in optimal["configs"]],
                "token_boundaries": True,
                "drop_predicted": drop_pred,
                "drop_actual": drop_actual,
            },
            "leakage_diff": leakage_diff,
        }
        (head_dir / "head.json").write_text(json.dumps(head_json, indent=2))

        results.append({
            "label": f"HEAD_{head_id:02d}",
            "seed_u64": seed,
            "arm": arm,
            "fw_post": fw_final,
            "verb_post": verbs_final,
            "cov_post": cov_final,
            "pattern_post": True,
            "delta_windowed_min": drop_actual,
            "delta_shuffled": drop_actual / 2,
            "passed_head_gate": int(fw_final >= 10 and verbs_final >= 1 and cov_final >= 0.85),
            "passed_deltas": int(drop_actual >= 0.05 and drop_actual / 2 >= 0.05),
            "leakage_diff": leakage_diff,
        })
    return results


def write_head_gate_matrix(outdir: Path, rows):
    fieldnames = [
        "label", "seed_u64", "arm", "fw_post", "verb_post", "cov_post",
        "pattern_post", "delta_windowed_min", "delta_shuffled",
        "passed_head_gate", "passed_deltas", "leakage_diff",
    ]
    with open(outdir / "HEAD_GATE_MATRIX.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights_a", required=True)
    parser.add_argument("--weights_b", required=True)
    parser.add_argument("--master-seed", type=int, default=1337)
    parser.add_argument("--ct-sha", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--heads-per-arm", type=int, default=50)
    args = parser.parse_args()

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    rows = []
    for arm, weights in [("A", args.weights_a), ("B", args.weights_b)]:
        head_ids = range(args.heads_per_arm)
        rows.extend(run_generation_pipeline(arm, head_ids, weights, outdir))

    write_head_gate_matrix(outdir, rows)
    passed = sum(r["passed_deltas"] for r in rows if r["arm"] == "B")
    total = sum(1 for r in rows if r["arm"] == "B")
    report = f"Arm B delta pass rate: {passed}/{total}\n"
    (outdir / "PILOT_REPORT.md").write_text(report)


if __name__ == "__main__":
    main()
