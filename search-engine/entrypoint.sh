set -x
mkdir -p storage/{uploads,index}
redis-server &
python3 codesearch/query/searcher.py storage/index &
cp -r codesearch storage/uploads
python3 codesearch/code/indexer.py storage/uploads storage/index &
browsepy 0.0.0.0 8080 --directory storage/uploads &
python3 codesearch/server.py 8000
