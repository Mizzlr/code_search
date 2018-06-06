import pandas as pd
import nmslib
from codesearch.query.encoder import encode_query_string
from codesearch.code.summarizer import summarize_code


class SemanticCodeSearchEngine:
    def __init__(self, search_index_dir):
        self.codebase_df = pd.read_feather(search_index_dir + '/codebase.df.feather')
        self.search_index = nmslib.init(method='hnsw', space='cosinesimil')
        self.search_index.loadIndex(search_index_dir + '/searchindex.nmslib')

    def search(self, query, num_result=10, summarize=True):
        embedding = encode_query_string(query)
        idxs, dists = self.search_index.knnQuery(embedding, k=num_result)

        results = []
        rank = 1

        for idx, dist in zip(idxs, dists):
            row = self.codebase_df[self.codebase_df.code_vec_hash == idx]
            if row.empty:
                row = self.codebase_df[self.codebase_df.comment_vec_hash == idx]

            row = row.iloc[0]
            if not row.empty:
                results.append({
                    'rank': rank,
                    'score': float(str(dist)),
                    'file': row.file_name,
                    'line': int(str(row.line)),
                    'code': row.function_body,
                    'summary': summarize_code(row.tokenized_body) if summarize else None,
                    'docstring': row.docstring
                })
                rank += 1

        return results


if __name__ == '__main__':
    import json
    import time
    import sys
    from codesearch.utils.redis_queue import RedisQueueExchange

    search_engine = SemanticCodeSearchEngine(sys.argv[1])
    queue_exchange = RedisQueueExchange()

    while True:
        while not queue_exchange.empty('input'):
            # pop query from the input queue
            query = queue_exchange.fetch('input')
            print('Found query:', query)
            # perform search and write result to output queue
            result = json.dumps(search_engine.search(query.replace('+', ' ')), indent=4)
            print('Writing results:', result)
            queue_exchange.write('output', query, result)
            queue_exchange.delete('input', query)
            pass

        # goto sleep for 100 milliseconds
        time.sleep(0.1)
