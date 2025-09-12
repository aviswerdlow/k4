from pathlib import Path
from experiments.pipeline_v4.scripts.v4_1.run_ab_pilot_production import run_generation_pipeline

WEIGHTS = "experiments/typo_tolerance/scripts/experiments/pipeline_v4/policies/experiments/pipeline_v4/scripts/v4.1/experiments/pipeline_v4/policies/weights.explore_v4_1.json"


def test_generation_quality(tmp_path):
    results = run_generation_pipeline("A", range(3), WEIGHTS, tmp_path)
    assert len(results) == 3
    for r in results:
        m = r
        assert m["fw_post"] >= 10
        assert m["verb_post"] >= 1
        assert m["cov_post"] >= 0.85
