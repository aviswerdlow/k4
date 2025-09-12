import subprocess
from pathlib import Path

WEIGHTS = "experiments/typo_tolerance/scripts/experiments/pipeline_v4/policies/experiments/pipeline_v4/scripts/v4.1/experiments/pipeline_v4/policies/weights.explore_v4_1.json"


def test_cli_production_limit(tmp_path):
    cmd = [
        "python",
        "experiments/pipeline_v4/scripts/v4_1/run_explore_v4_1_1_production.py",
        "--weights", WEIGHTS,
        "--ct-sha", "dummy",
        "--out", str(tmp_path),
        "--limit", "5",
    ]
    subprocess.run(cmd, check=True)
    assert (tmp_path / "EXPLORE_MATRIX.csv").exists()
