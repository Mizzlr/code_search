import redis


class RedisQueueExchange:
    """ Abstracts out redis interaction by unified api to store queue as
    both list and dict.
    """
    def __init__(self):
        self.db = redis.StrictRedis()

    def empty(self, queue):
        """Return true if a queue has no elements
        """
        return self.db.llen(queue) == 0

    def write(self, queue, key, value=None):
        """Write the key (optionally value) to list (or dict) in redis.
        """
        self.db.lpush(queue, key)
        if value:
            self.db.hset(queue + 'map', key, value)

    def delete(self, queue, key=None):
        """Delete an entry from the queue by key, if key is not provided
        then delete all entries in the queue.
        """
        if key:
            self.db.lrem(queue, -1, key)
            self.db.hdel(queue + 'map', key)
        else:
            self.db.delete(queue)
            self.db.delete(queue + 'map')

    def fetch(self, queue, key=None):
        """Fetch an element in the queue by key, if key is not provided
        then fetch the earliest element inserted
        """
        if key:
            return self.db.hget(queue + 'map', key)
        return self.db.lindex(queue, -1)


if __name__ == '__main__':
    exchange = RedisQueueExchange()
    exchange.write('input', 'test+query')
    exchange.write('input', 'test+query2')
    exchange.write('input', 'test+query3')
    print(exchange.empty('input'))
    print(exchange.fetch('input'))
    exchange.delete('input', 'test+query')
    print(exchange.empty('input'))
    print(exchange.db.lrange('input', 0, -1))
    print(exchange.fetch('input'))
    exchange.delete('input')
    print(exchange.empty('input'))

    exchange.write('output', 'test+query', 'result')
    exchange.write('output', 'test+query2', 'result2')
    exchange.write('output', 'test+query3', 'result3')
    print(exchange.empty('output'))
    print(exchange.db.lrange('output', 0, -1))
    print('==>', exchange.fetch('output', 'test+query2'))
    exchange.delete('output', 'test+query2')
    print(exchange.empty('output'))
    print(exchange.db.lrange('output', 0, -1))
    print(exchange.fetch('output'))
    exchange.delete('output')
    print(exchange.empty('output'))
