"""Package the KT3 submission, excluding compiled and temporary files."""
from pathlib import Path
from shutil import copy2
from subprocess import run
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
NAME = 'ИКБО-10-24_БикташевИИ_КТ3'
DESTINATION = ROOT.parent / NAME
ARCHIVE = ROOT.parent / (NAME + '.zip')
REPORT = 'Отчет_ИКБО-10-24_БикташевИИ_КТ3.docx'


def main():
    files = {REPORT: ROOT / REPORT, 'review/review.md': ROOT / 'review/review.md',
             'vcs/repo_url.txt': ROOT / 'repo_url.txt'}
    for path in (ROOT / 'models').iterdir():
        if path.suffix in {'.puml', '.png', '.drawio', '.bpmn'}:
            files[str(path.relative_to(ROOT))] = path
    for path in (ROOT / 'src/java').rglob('*'):
        relative = path.relative_to(ROOT)
        if path.is_file() and not {'out', 'build', 'target', '__pycache__'} & set(relative.parts):
            if path.suffix not in {'.class', '.pyc'} and path.name != '.DS_Store':
                files[str(relative)] = path
    expected = set(files) | {'vcs/git_log.txt'}
    if DESTINATION.exists():
        extras = {str(p.relative_to(DESTINATION)) for p in DESTINATION.rglob('*') if p.is_file()} - expected
        if extras:
            raise RuntimeError(f'Unexpected files in submission: {sorted(extras)}')
    for relative, source in files.items():
        target = DESTINATION / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        copy2(source, target)
    history = run(['git', '-C', str(ROOT), 'log', '--all', '--date=iso',
                   '--pretty=format:%h %ad %an %s'], check=True,
                  capture_output=True, text=True, encoding='utf-8').stdout + '\n'
    (DESTINATION / 'vcs/git_log.txt').write_text(history, encoding='utf-8')
    temporary = ARCHIVE.with_suffix('.tmp.zip')
    with ZipFile(temporary, 'w', ZIP_DEFLATED) as archive:
        for name in sorted(expected):
            archive.write(DESTINATION / name, name)
    temporary.replace(ARCHIVE)
    with ZipFile(ARCHIVE) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == expected
        assert not any(name.endswith(('.class', '.pyc')) or '/out/' in name for name in expected)
        assert 'src/main.py' not in expected
    print(f'{ARCHIVE}\nFiles: {len(expected)}; bytes: {ARCHIVE.stat().st_size}')


if __name__ == '__main__':
    main()
