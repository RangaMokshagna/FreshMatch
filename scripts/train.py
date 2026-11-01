"""Execute FreshMatch's source notebook with the active, pinned interpreter."""
from pathlib import Path
import os
import argparse
import sys
import nbformat
from nbclient import NotebookClient
from importlib.metadata import version
from sync_notebook import check

ROOT = Path(__file__).resolve().parents[1]
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-source', choices=['instacart', 'synthetic'], default=os.environ.get('FRESHMATCH_DATA_SOURCE', 'instacart'))
    parser.add_argument('--data-dir', type=Path, default=Path(os.environ.get('FRESHMATCH_DATA_DIR', ROOT/'instacart')))
    parser.add_argument('--check-data', action='store_true', help='Validate real CSV files without training or changing inference artifacts')
    args = parser.parse_args()
    os.environ['FRESHMATCH_DATA_SOURCE'] = args.data_source
    os.environ['FRESHMATCH_DATA_DIR'] = str(args.data_dir.expanduser().resolve())
    sys.path.insert(0, str(ROOT))
    if args.data_source == 'instacart':
        from real_data import validate_instacart, DatasetError
        try:
            directory = validate_instacart(args.data_dir)
        except DatasetError as exc:
            parser.exit(2, f'{exc}\n')
        print(f'Validated Instacart schemas and sample rows in {directory}', flush=True)
    elif args.check_data:
        parser.error('--check-data requires --data-source instacart')
    if args.check_data:
        raise SystemExit(0)
    check()  # Refuse to overwrite Python edits that have not been embedded yet.
    for line in (ROOT / 'requirements.txt').read_text().splitlines():
        if '==' in line:
            name, expected = line.split('==')
            if version(name) != expected:
                raise SystemExit(f'{name}: expected {expected}. Install requirements.txt with {sys.executable}.')
    os.environ['FRESHMATCH_SKIP_LAUNCH'] = '1'
    for name in ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS']:
        os.environ[name] = '2'
    cache = ROOT / '.cache_freshmatch'
    cache.mkdir(exist_ok=True)
    os.environ['MPLCONFIGDIR'] = str(cache / 'matplotlib')
    os.environ['JUPYTER_RUNTIME_DIR'] = str(cache / 'jupyter')
    notebook = nbformat.read(ROOT / 'product_substitution.ipynb', as_version=4)
    # Requirements were checked above; do not reinstall from an executing kernel.
    for cell in notebook.cells:
        if cell.cell_type == 'code' and cell.source.startswith('%pip '):
            cell.source = "print('Exact project dependency versions verified by scripts/train.py')"
    def progress(cell, cell_index, **kwargs):
        if cell.cell_type == 'code':
            print(f'Executing cell {cell_index}: {cell.source.splitlines()[0][:90]}', flush=True)
    client = NotebookClient(notebook, timeout=1200, kernel_name='python3',
        resources={'metadata': {'path': str(ROOT)}}, on_cell_start=progress)
    try:
        client.execute()
    finally:
        nbformat.write(notebook, cache / 'executed.ipynb')
    for cell in notebook.cells:
        for out in cell.get('outputs', []):
            if out.output_type == 'stream':
                print(out.text, end='')
    print('\nPASS: notebook training, artifact generation and integrity assertions')
