FROM python:latest

RUN apt-get update -y && apt-get install -y redis-tools redis-server \
    unzip tree curl

RUN pip3 install spacy
RUN python3 -m spacy download en

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

WORKDIR /app/

# download model files from internet
RUN mkdir -p codesearch/.data/{code2emb,lang_model,seq2seq}
RUN curl https://storage.googleapis.com/kubeflow-examples/code_search/data/code2emb/code2emb_model.hdf5 > codesearch/.data/code2emb/code2emb_model.hdf5
RUN curl https://storage.googleapis.com/kubeflow-examples/code_search/data/lang_model/lang_model_cpu_v2.torch > codesearch/.data/lang_model/lang_model_cpu_v2.torch
RUN curl https://storage.googleapis.com/kubeflow-examples/code_search/data/lang_model/vocab_v2.cls > codesearch/.data/lang_model/vocab_v2.cls
RUN curl https://storage.googleapis.com/kubeflow-examples/code_search/data/seq2seq/py_code_proc_v2.dpkl > codesearch/.data/seq2seq/py_code_proc_v2.dpkl
RUN curl https://storage.googleapis.com/kubeflow-examples/code_search/data/seq2seq/py_comment_proc_v2.dpkl > codesearch/.data/seq2seq/py_comment_proc_v2.dpkl
RUN curl https://storage.googleapis.com/kubeflow-examples/code_search/data/seq2seq/py_func_sum_v9_.epoch16-val2.55276.hdf5 > codesearch/.data/seq2seq/py_func_sum_v9_.epoch16-val2.55276.hdf5

# copy the source code
COPY codesearch/ codesearch/
COPY entrypoint.sh indexer.sh /app/
RUN chmod +x entrypoint.sh indexer.sh

CMD ["/bin/bash", "-c", "./entrypoint.sh"]
