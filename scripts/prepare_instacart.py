"""Extract an official Kaggle ZIP safely, including nested *.csv.zip payloads."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from real_data import DatasetError, extract_instacart_archive

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT/'instacart')
    args = parser.parse_args()
    try:
        path = extract_instacart_archive(args.archive, args.output)
    except (DatasetError, OSError) as exc:
        parser.exit(2, f'{exc}\n')
    print(f'Extracted and validated the five required CSV files in {path}')
    print('Next: python scripts/train.py --data-source instacart --data-dir ' + str(path.resolve()))
