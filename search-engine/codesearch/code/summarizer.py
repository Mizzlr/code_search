from keras.models import load_model
from pathlib import Path
from codesearch.utils.seq2seq_utils import load_text_processor, Seq2Seq_Inference


seq2seq_path = Path('codesearch/.data/seq2seq/')
seq2seq_Model = load_model(seq2seq_path / 'py_func_sum_v9_.epoch16-val2.55276.hdf5')
num_encoder_tokens, enc_pp = load_text_processor(seq2seq_path / 'py_code_proc_v2.dpkl')
num_decoder_tokens, dec_pp = load_text_processor(seq2seq_path / 'py_comment_proc_v2.dpkl')

seq2seq_inf = Seq2Seq_Inference(encoder_preprocessor=enc_pp,
                                decoder_preprocessor=dec_pp,
                                seq2seq_model=seq2seq_Model)

__all__ = ['summarize_code']


def summarize_code(code_string, max_len=None):
    return seq2seq_inf.predict(code_string, max_len)[1]


if __name__ == '__main__':
    no_docstring_funcs = ['def __init__ self leafs edges self edges edges self leafs sorted leafs\n',
     'def __eq__ self other if isinstance other Node return id self id other or self leafs other leafs and self edges other edges else return False\n',
     'def __repr__ self return Node leafs edges format self leafs self edges\n',
     'staticmethod def _isCapitalized token return len token 1 and token isalpha and token 0 isupper and token 1 islower\n',
     'staticmethod def _isCapitalizeD last token return last and len token 1 and last isalpha and token isupper\n']

    for code_string in no_docstring_funcs:
        print(code_string)
        print(summarize_code(code_string))
