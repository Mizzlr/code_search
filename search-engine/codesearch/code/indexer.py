from codesearch.utils.general_utils import create_nmslib_search_index
from codesearch.code.parser import create_codebase_dataframe
from codesearch.code.encoder import encode_code_to_natural_lang
from codesearch.query.encoder import encode_doc_strings
from pathlib import Path
import numpy as np


def run_indexing_pipeline(codebase_root_dir, index_dump_dir):

    codebase_root_dir = Path(codebase_root_dir)

    codebase_df = create_codebase_dataframe(codebase_root_dir)
    code_vecs = encode_code_to_natural_lang(codebase_df['tokenized_body'])
    comment_vecs = encode_doc_strings(codebase_df['docstring'])

    # codebase_df['code_vec'] = code_vecs
    # codebase_df['comment_vec'] = comment_vecs

    code_vecs.flags.writeable = False
    comment_vecs.flags.writeable = False

    codebase_df['code_vec_hash'] = np.nan
    codebase_df['comment_vec_hash'] = np.nan

    all_vectors = []

    for i, row in codebase_df.iterrows():
        all_vectors.append(code_vecs[i, :])
        codebase_df.loc[i, 'code_vec_hash'] = len(all_vectors) - 1  # hash(code_vecs[i, :].data.tobytes())

        if row['docstring']:
            all_vectors.append(comment_vecs[i, :])
            codebase_df.loc[i, 'comment_vec_hash'] = len(all_vectors) - 1  # hash(comment_vecs[i, :].data.tobytes())

    index_dump_dir = Path(index_dump_dir)
    searchIndex = create_nmslib_search_index(np.asarray(all_vectors))

    searchIndex.saveIndex(str(index_dump_dir / 'searchindex.nmslib'))
    codebase_df.to_feather((index_dump_dir / 'codebase.df.feather').open('wb'))


if __name__ == '__main__':
    # codebase_root_dir = Path(__file__).absolute().parent.parent
    # codebase_root_dir = 'uploads'
    import sys
    run_indexing_pipeline(sys.argv[1], sys.argv[2])
