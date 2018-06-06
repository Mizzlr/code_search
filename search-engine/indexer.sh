set -x
unzip -r storage/uploads/*.zip -d storage/uploads
fkill -9 "python3 codesearch/code/indexer.py storage/uploads storage/index"
fkill -9 "python3 codesearch/query/searcher.py storage/index"
rm storage/uploads/*.zip
rm storage/index/*
python3 codesearch/code/indexer.py storage/uploads storage/index
python3 codesearch/query/searcher.py storage/index &
