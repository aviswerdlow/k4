import subprocess, sys, os, pathlib, json

def run(cmd):
    return subprocess.check_output(cmd, shell=True, text=True).strip()

def test_plaintext97():
    out = run("python k4_cli.py")
    assert len(out) == 97
    assert out.startswith("HAVINGSETYOURCOURSEGOEASTNORTHEASTTHENPROCEED")
    assert out.endswith("HENCEOFANANGLEISTHEARC")

def test_vector():
    out = run("python k4_cli.py --vector")
    assert "Go 5.0000 rods on bearing N 61.6959° E" in out
