"""Synchronize the editable Python sources with notebook writefile cells."""
from pathlib import Path
import argparse
import nbformat

ROOT = Path(__file__).resolve().parents[1]

def check():
    nb = nbformat.read(ROOT / 'product_substitution.ipynb', as_version=4)
    for filename in ['app.py', 'advanced_ml.py']:
        expected = f'%%writefile {filename}\n' + (ROOT / filename).read_text()
        matches = [c for c in nb.cells if c.cell_type == 'code' and c.source.startswith(f'%%writefile {filename}\n')]
        if len(matches) != 1 or matches[0].source != expected:
            raise SystemExit(f'{filename} differs from the notebook. Review edits, then run python scripts/sync_notebook.py before training.')


def sync():
    path = ROOT / 'product_substitution.ipynb'
    nb = nbformat.read(path, as_version=4)
    for filename in ['app.py', 'advanced_ml.py']:
        matches = [c for c in nb.cells if c.cell_type == 'code' and c.source.startswith(f'%%writefile {filename}\n')]
        if len(matches) != 1:
            raise ValueError(f'Expected exactly one notebook cell writing {filename}')
        matches[0].source = f'%%writefile {filename}\n' + (ROOT / filename).read_text()
    for cell in nb.cells:
        if cell.cell_type == 'code':
            cell.outputs = []
            cell.execution_count = None
    nbformat.write(nb, path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check synchronization without modifying files')
    args = parser.parse_args()
    check() if args.check else sync()
