from codesearch.utils.general_utils import create_nmslib_search_index
from codesearch.utils.vector_utils import hash_vector, union_vectors
from codesearch.code.parser import create_codebase_dataframe
from codesearch.code.encoder import encode_code_to_natural_lang
from codesearch.query.encoder import encode_doc_strings
from pathlib import Path


def run_indexing_pipeline(codebase_root_dir, index_dump_dir):

    index_dump_dir = Path(index_dump_dir)

    codebase_files_df = create_codebase_files_dataframe(codebase_root_dir)
    codebase_df = create_codebase_dataframe(codebase_files_df)
    code_vecs = encode_code_to_natural_lang(codebase_df['tokenized_code_snippet'])
    comment_vecs = encode_doc_strings(codebase_df['doc_string']) * codebase_df['doc_string']
    codebase_df['code_vecs_hash'] = hash_vector(code_vecs)
    codebase_df['comment_vecs_hash'] = hash_vector(comment_vecs)

    searchIndex = create_nmslib_search_index(union_vectors(code_vecs, comment_vecs))
    searchIndex.saveIndex(index_dump_dir / 'searchindex.nmslib')
    codebase_df.write_csv(index_dump_dir / 'codebase.dataframe')
