from experiments.pipeline_v4.scripts.v4_1.run_ab_pilot_production import run_generation_pipeline
from experiments.pipeline_v4.scripts.v4_1.run_explore_v4_1_1_production import run_orbit_isolation, run_fast_nulls

WEIGHTS = "experiments/typo_tolerance/scripts/experiments/pipeline_v4/policies/experiments/pipeline_v4/scripts/v4.1/experiments/pipeline_v4/policies/weights.explore_v4_1.json"


def test_orbit_and_nulls(tmp_path):
    run_generation_pipeline("A", [0], WEIGHTS, tmp_path)
    head_dir = tmp_path / "generation" / "HEAD_00_A"
    iso = run_orbit_isolation(head_dir, n_neighbors=10)
    assert iso["n_neighbors"] == 10
    nulls = run_fast_nulls(head_dir, K=100)
    assert "p_holm" in nulls
