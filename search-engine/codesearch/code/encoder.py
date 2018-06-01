from keras.models import load_model
from pathlib import Path
from codesearch.utils.seq2seq_utils import load_text_processor
from typing import List

code2emb_path = Path('codesearch/.data/code2emb/')
seq2seq_path = Path('codesearch/.data/seq2seq/')

code2emb_model = load_model(code2emb_path / 'code2emb_model.hdf5')
num_encoder_tokens, enc_pp = load_text_processor(seq2seq_path / 'py_code_proc_v2.dpkl')

__all__ = ['encode_code_to_natural_lang']


def encode_code_to_natural_lang(code_strings: List[str]):
    return code2emb_model.predict(enc_pp.transform_parallel(code_string), batch_size=20000)


if __name__ == '__main__':
    no_docstring_funcs = ['def __init__ self leafs edges self edges edges self leafs sorted leafs\n',
     'def __eq__ self other if isinstance other Node return id self id other or self leafs other leafs and self edges other edges else return False\n',
     'def __repr__ self return Node leafs edges format self leafs self edges\n',
     'staticmethod def _isCapitalized token return len token 1 and token isalpha and token 0 isupper and token 1 islower\n',
     'staticmethod def _isCapitalizeD last token return last and len token 1 and last isalpha and token isupper\n']

    for code_string in no_docstring_funcs:
        print(code_string)
        encode_code_to_natural_lang(code_string)
