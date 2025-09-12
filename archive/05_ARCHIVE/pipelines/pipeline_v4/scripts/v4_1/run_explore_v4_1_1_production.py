import argparse
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[4]))
import json
import csv
import hashlib
from pathlib import Path
import random

from experiments.pipeline_v4.scripts.v4_1.multi_objective_mcmc import MultiObjectiveMCMC
from experiments.pipeline_v4.scripts.v4_1.saliency_map import SaliencyMapper
from experiments.pipeline_v4.scripts.v4_1.run_ab_pilot_production import run_generation_pipeline


def run_orbit_isolation(candidate_dir: Path, n_neighbors: int = 50):
    candidate_dir = Path(candidate_dir)
    with open(candidate_dir / "head.json") as f:
        head = json.load(f)
    text = head["text_final"]
    mapper = SaliencyMapper()
    sal_map = mapper.generate_saliency_map(text)
    char_sal = sal_map["char_saliency"]
    low_idx = sorted(range(len(char_sal)), key=lambda i: char_sal[i])[:max(1, len(char_sal)//3)]
    mcmc = MultiObjectiveMCMC()
    base_score = mcmc.compute_objective(text)

    neighbors = []
    for n in range(n_neighbors):
        pos = low_idx[n % len(low_idx)]
        neighbor_text = text[:pos] + " THE " + text[pos:]
        delta = base_score - mcmc.compute_objective(neighbor_text)
        neighbors.append((n, delta))

    tie_fraction = sum(1 for _, d in neighbors if abs(d) <= 0.01) / len(neighbors)
    orbit_dir = candidate_dir / "orbits" / f"{head['head_id']}_{head['arm']}"
    orbit_dir.mkdir(parents=True, exist_ok=True)
    with open(orbit_dir / "ORBIT_SUMMARY.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["neighbor_id", "delta", "tie"])
        for nid, delta in neighbors:
            writer.writerow([nid, delta, int(abs(delta) <= 0.01)])
    return {"is_isolated": tie_fraction <= 0.15, "tie_fraction": tie_fraction, "n_neighbors": len(neighbors)}


def run_fast_nulls(candidate_dir: Path, K: int = 1000):
    candidate_dir = Path(candidate_dir)
    with open(candidate_dir / "head.json") as f:
        head = json.load(f)
    text = head["text_final"]
    mcmc = MultiObjectiveMCMC()
    base_cov = mcmc.calculate_coverage(text)
    base_fw = mcmc.count_function_words(text)

    cov_ge = 0
    fw_ge = 0
    for _ in range(K):
        null_text = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ ') for _ in range(len(text)))
        if mcmc.calculate_coverage(null_text) >= base_cov:
            cov_ge += 1
        if mcmc.count_function_words(null_text) >= base_fw:
            fw_ge += 1
    p_cov = (cov_ge + 1) / (K + 1)
    p_fw = (fw_ge + 1) / (K + 1)
    # Holm m=2
    if p_cov > p_fw:
        adj_cov = min(1.0, p_cov * 2)
        adj_fw = min(1.0, max(p_fw, p_cov))
    else:
        adj_fw = min(1.0, p_fw * 2)
        adj_cov = min(1.0, max(p_cov, p_fw))
    result = {
        "counts_ge": {"coverage": cov_ge, "f_words": fw_ge},
        "p_raw": {"coverage": p_cov, "f_words": p_fw},
        "p_holm": {"coverage": adj_cov, "f_words": adj_fw},
        "publishable": adj_cov < 0.01 and adj_fw < 0.01,
    }
    out_dir = candidate_dir / "fast_nulls"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "holm_report.json").write_text(json.dumps(result, indent=2))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights", required=True)
    parser.add_argument("--master-seed", type=int, default=1337)
    parser.add_argument("--ct-sha", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--limit", type=int, default=200)
    args = parser.parse_args()

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    rows = run_generation_pipeline("B", range(args.limit), args.weights, outdir)
    with open(outdir / "EXPLORE_MATRIX.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


if __name__ == "__main__":
    main()
