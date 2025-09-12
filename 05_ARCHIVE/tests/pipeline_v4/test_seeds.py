from experiments.pipeline_v4.scripts.v4_1.run_ab_pilot_production import derive_seed


def test_seed_determinism():
    s1 = derive_seed(0, "A")
    s2 = derive_seed(0, "A")
    assert s1 == s2
    assert derive_seed(1, "A") != s1
    assert derive_seed(0, "B") != s1
