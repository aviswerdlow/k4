import subprocess
from pathlib import Path
from experiments.pipeline_v4.scripts.v4_1.run_ab_pilot_production import run_generation_pipeline

WEIGHTS = "experiments/typo_tolerance/scripts/experiments/pipeline_v4/policies/experiments/pipeline_v4/scripts/v4.1/experiments/pipeline_v4/policies/weights.explore_v4_1.json"


def test_validator(tmp_path):
    run_generation_pipeline("A", [0], WEIGHTS, tmp_path)
    head_dir = tmp_path / "generation" / "HEAD_00_A"
    subprocess.run(
        ["python", "scripts/tools/validate_bundle.py", str(head_dir), "--schema", "scripts/schema", "--mode", "lenient"],
        check=True,
    )
