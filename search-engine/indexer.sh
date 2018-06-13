set -x
# unzip any zip files in storage/uploads
unzip -o storage/uploads/*.zip -d storage/uploads

# stop the search engine and previously running indexer if any
ps -ef | grep codesearch/query/searcher.py | grep -v grep | awk '{print $2}' | xargs kill -9
ps -ef | grep codesearch/code/indexer.py | grep -v grep | awk '{print $2}' | xargs kill -9

# clean up any uploaded zip files and all the files in storage/index folder
rm storage/uploads/*.zip
rm storage/index/*

# start the semantic indexer process
python3 codesearch/code/indexer.py storage/uploads storage/index

# start the semantic code search engine back
python3 codesearch/query/searcher.py storage/index &
