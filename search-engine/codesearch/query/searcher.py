from collections import namedtuple

SearchResult = namedtuple('SearchResult', 'rank, score, file, line, code, summary')


class SemanticCodeSearchEngine:
    def __init__(searchIndexDir):
        pass

    def search(query, summarize=True):
        pass
