import subprocess
from pathlib import Path

WEIGHTS = "experiments/typo_tolerance/scripts/experiments/pipeline_v4/policies/experiments/pipeline_v4/scripts/v4.1/experiments/pipeline_v4/policies/weights.explore_v4_1.json"


def test_cli_pilot(tmp_path):
    cmd = [
        "python",
        "experiments/pipeline_v4/scripts/v4_1/run_ab_pilot_production.py",
        "--weights_a", WEIGHTS,
        "--weights_b", WEIGHTS,
        "--ct-sha", "dummy",
        "--out", str(tmp_path),
        "--heads-per-arm", "3",
    ]
    subprocess.run(cmd, check=True)
    assert (tmp_path / "HEAD_GATE_MATRIX.csv").exists()
