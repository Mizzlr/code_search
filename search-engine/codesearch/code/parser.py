from pathlib import Path
from codesearch.utils.parser_utils import get_function_docstring_pairs_list
import pandas as pd
import json


def create_codebase_dataframe(codebase_dir):
    codebase_dir = Path(codebase_dir)
    python_files = list(codebase_dir.glob('**/*.py'))
    blobs = [python_file.open('r').read() for python_file in python_files]
    pairs = get_function_docstring_pairs_list(blobs)
    python_files = [python_file.name for python_file in python_files]
    print(pairs)
    print(python_files)
    return json.dumps(dict(zip(python_files, pairs)), indent=4)


if __name__ == '__main__':
    print(create_codebase_dataframe(Path(__file__).absolute().parent))
