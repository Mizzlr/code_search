from pathlib import Path
from codesearch.utils.parser_utils import get_function_docstring_pairs
import pandas as pd


def create_codebase_dataframe(codebase_dir):
    codebase_dir = Path(codebase_dir)
    python_files = list(codebase_dir.glob('**/*.py'))

    codebase_data = []
    for python_file in python_files:
        blob = python_file.open('r').read()
        for pair in get_function_docstring_pairs(blob):
            file_name = str(python_file.absolute())
            function_name, line_no, function_body, tokenized_body, docstring = pair
            codebase_data.append({
                'file_name': file_name,
                'function_name': function_name,
                'function_body': function_body,
                'tokenized_body': tokenized_body,
                'docstring': docstring
            })

    return pd.DataFrame(codebase_data)


if __name__ == '__main__':
    print(create_codebase_dataframe(Path(__file__).absolute().parent.parent).to_csv(open('codebase.csv', 'w')))
