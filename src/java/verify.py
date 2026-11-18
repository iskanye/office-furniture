"""Run Java against expected Python results and the Python version if available."""
from pathlib import Path
import copy, importlib.util, json, subprocess, tempfile
HERE = Path(__file__).resolve().parent
cases = json.loads((HERE / "tests/cases.json").read_text(encoding="utf-8"))
procedural = HERE.parent / "main.py"
module = None
if procedural.exists():
    spec = importlib.util.spec_from_file_location("procedural", procedural)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
for case in cases:
    if module:
        assert module.process_request(copy.deepcopy(case["input"])) == case["expected"], case["name"]
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / "input.json"
        source.write_text(json.dumps(case["input"], ensure_ascii=False), encoding="utf-8")
        result = subprocess.run(["java", "-cp", str(HERE / "out"), "Main", str(source)],
                                capture_output=True, text=True, check=True)
        assert json.loads(result.stdout) == case["expected"], (case["name"], result.stdout)
print(f"OK: {len(cases)} scenarios; Python comparison: {module is not None}")
