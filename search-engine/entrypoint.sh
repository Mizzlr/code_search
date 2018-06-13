set -x
# clean up storage folders, if any from previous run
rm -rf storage

# create folders for uploaded files and semantic index
mkdir -p storage/{uploads,index}

# start redis message queue, used to ipc between server and search engine
redis-server &

# start the semantic code search engine service pointing to storage/index
python3 codesearch/query/searcher.py storage/index &

# dogfood the source code of semantic code search
cp -r codesearch storage/uploads

# semantically index the files in storage/uploads and dump the index into storage/index
python3 codesearch/code/indexer.py storage/uploads storage/index &

# start the python webserver at port 8000
python3 codesearch/server.py 8000
