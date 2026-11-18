import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location(
    'aara_validate', Path(__file__).resolve().parent.parent / 'scripts' / 'validate.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_rejects_todo(tmp_path):
    p = tmp_path / 'r.md'
    p.write_text("- status: NEW\n- item: TODO\n", encoding="utf-8")
    assert mod.validate(str(p))


def test_accepts_clean(tmp_path):
    p = tmp_path / 'r.md'
    p.write_text("- status: BASELINED\n- item: SYS-001\n", encoding="utf-8")
    assert mod.validate(str(p)) == []
