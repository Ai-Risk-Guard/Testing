from pathlib import Path


def test_lab_configuration_contains_synthetic_hardcoded_secret():
    """
    Baseline test for the intentionally hardcoded demonstration secret.

    After moving the secret to an environment variable, update this
    test to verify that the literal no longer exists in config.py.
    """

    project_root = Path(__file__).resolve().parents[1]

    config_path = project_root / "config.py"

    source = config_path.read_text(
        encoding="utf-8"
    )

    assert (
        "AUREX_LAB_DEMO_SECRET_12345"
        in source
    )