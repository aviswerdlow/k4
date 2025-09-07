from experiments.pipeline_v4.scripts.v4_1.run_ab_pilot_production import run_generation_pipeline

WEIGHTS = "experiments/typo_tolerance/scripts/experiments/pipeline_v4/policies/experiments/pipeline_v4/scripts/v4.1/experiments/pipeline_v4/policies/weights.explore_v4_1.json"


def test_leakage(tmp_path):
    res = run_generation_pipeline("A", [0], WEIGHTS, tmp_path)[0]
    assert abs(res["leakage_diff"]) == 0
