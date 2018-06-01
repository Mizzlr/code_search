import sys
import torch
from codesearch.utils.lang_model_utils import load_lm_vocab, get_embeddings
from codesearch.utils import lang_model_utils


sys.modules['lang_model_utils'] = lang_model_utils
lang_model = torch.load('codesearch/.data/lang_model/lang_model_cpu_v2.torch',
                        map_location=lambda storage, loc: storage)
vocab = load_lm_vocab('codesearch/.data/lang_model/vocab_v2.cls')


def encode_query_string(query_string):
    idx_docs = vocab.transform([query_string], max_seq_len=30, padding=False)
    avg_emb, max_emb, last_emb = get_embeddings(lang_model, idx_docs)
    return avg_emb[0]


if __name__ == '__main__':
    docstrings = ['"generates batches of samples : param data : array - like , shape = ( n_samples , n_features ) : param labels : array - like , shape = ( n_samples , ) : return :"\n',
        '"converts labels as single integer to row vectors . for instance , given a three class problem , labels would be mapped as label_1 : [ 1 0 0 ] , label_2 : [ 0 1 0 ] , label_3 : [ 0 , 0 , 1 ] where labels can be either int or string . : param labels : array - like , shape = ( n_samples , ) : return :"\n',
        '"sigmoid function . : param x : array - like , shape = ( n_features , ) : return :"\n',
        '"compute sigmoid first derivative . : param x : array - like , shape = ( n_features , ) : return :"\n',
        '"rectified linear function . : param x : array - like , shape = ( n_features , ) : return :"\n',
        '"rectified linear first derivative . : param x : array - like , shape = ( n_features , ) : return :"\n',
        '"hyperbolic tangent function . : param x : array - like , shape = ( n_features , ) : return :"\n',
        '"hyperbolic tangent first derivative . : param x : array - like , shape = ( n_features , ) : return :"\n',
        'blueflask command line .\n',
        'args : name ( str ) : app name . directory ( str ) : path of the directory where the project is going to be created . defaults to the current directory .\n'
    ]

    for docstring in docstrings:
        print(docstring)
        # print(encode_query_string(docstring))
