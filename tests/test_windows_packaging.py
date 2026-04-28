from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_windows_build_and_verify_scripts_are_documented():
    build_script = ROOT / "scripts" / "build_windows.ps1"
    verify_script = ROOT / "scripts" / "verify_dist.ps1"
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert build_script.exists()
    assert verify_script.exists()
    assert "scripts/build_windows.ps1" in readme
    assert "scripts/verify_dist.ps1" in readme


def test_verify_dist_blocks_known_dll_pollution_patterns():
    verify_script = (ROOT / "scripts" / "verify_dist.ps1").read_text(encoding="utf-8")

    assert "icu*.dll" in verify_script
    assert "Anaconda" in verify_script
    assert "MSYS2" in verify_script
    assert "Git\\usr\\bin" in verify_script
    assert "startup-error.log" in verify_script


def test_build_script_uses_clean_windows_path():
    build_script = (ROOT / "scripts" / "build_windows.ps1").read_text(encoding="utf-8")

    assert "PYTHONNOUSERSITE" in build_script
    assert ".venv\\Scripts" in build_script
    assert "C:\\Windows\\System32" in build_script
    assert "pyinstaller" in build_script
    assert "verify_dist.ps1" in build_script
