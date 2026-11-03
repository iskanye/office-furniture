"""Assemble the KT2 submission tree and ZIP exactly as specified in the memo."""

from pathlib import Path
from shutil import copy2
from subprocess import run
from zipfile import ZipFile, ZIP_DEFLATED


ROOT = Path(__file__).resolve().parents[2]
REPOSITORY = ROOT / "vcs"
SUBMISSION = ROOT / "ИКБО-10-24_БикташевИИ_КТ2"
ARCHIVE = ROOT / "ИКБО-10-24_БикташевИИ_КТ2.zip"

FILES = {
    "report.docx": REPOSITORY / "Отчет_ИКБО-10-24_БикташевИИ.docx",
    "models/bpmn.bpmn": REPOSITORY / "models/bpmn.bpmn",
    "models/bpmn.png": REPOSITORY / "models/bpmn.png",
    "models/er_logical.drawio": REPOSITORY / "models/er_logical.drawio",
    "models/er_logical.png": REPOSITORY / "models/er_logical.png",
    "models/algo_1.drawio": REPOSITORY / "models/algo_1.drawio",
    "models/algo_1.png": REPOSITORY / "models/algo_1.png",
    "models/algo_2.drawio": REPOSITORY / "models/algo_2.drawio",
    "models/algo_2.png": REPOSITORY / "models/algo_2.png",
    "src/README.md": REPOSITORY / "src/README.md",
    "src/main.py": REPOSITORY / "src/main.py",
    "src/example.json": REPOSITORY / "src/example.json",
    "src/example_cancel.json": REPOSITORY / "src/example_cancel.json",
    "vcs/repo_url.txt": REPOSITORY / "repo_url.txt",
}


def main():
    expected = {Path(name) for name in FILES} | {Path("vcs/git_log.txt")}
    if SUBMISSION.exists():
        unexpected = {
            path.relative_to(SUBMISSION)
            for path in SUBMISSION.rglob("*")
            if path.is_file() and path.relative_to(SUBMISSION) not in expected
        }
        if unexpected:
            raise SystemExit(f"Unexpected files in submission: {sorted(unexpected)}")

    for name, source in FILES.items():
        if not source.is_file():
            raise SystemExit(f"Missing source: {source}")
        destination = SUBMISSION / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        copy2(source, destination)

    history = run(
        ["git", "-C", str(REPOSITORY), "log", "--all", "--date=iso",
         "--pretty=format:%h %ad %an %s"],
        check=True, capture_output=True, text=True, encoding="utf-8",
    ).stdout
    (SUBMISSION / "vcs/git_log.txt").write_text(history, encoding="utf-8")

    temporary = ARCHIVE.with_suffix(".tmp.zip")
    with ZipFile(temporary, "w", ZIP_DEFLATED) as archive:
        for name in sorted(str(path) for path in expected):
            archive.write(SUBMISSION / name, name)
    temporary.replace(ARCHIVE)

    with ZipFile(ARCHIVE) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == {str(path) for path in expected}
    print(SUBMISSION)
    print(ARCHIVE)


if __name__ == "__main__":
    main()
