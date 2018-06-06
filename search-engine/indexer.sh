set -x
unzip -r storage/uploads/*.zip -d storage/uploads
ps -ef | grep codesearch/query/searcher.py | grep -v grep | awk '{print $2}' | xargs kill -9
ps -ef | grep codesearch/code/indexer.py | grep -v grep | awk '{print $2}' | xargs kill -9
rm storage/uploads/*.zip
rm storage/index/*
python3 codesearch/code/indexer.py storage/uploads storage/index
python3 codesearch/query/searcher.py storage/index &
