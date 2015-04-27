"""
Application caching

Caching and related classes
"""
import memcache
import cPickle
#import redis


class CacheHandler():
    """
    Abstract base class that should be implemented by all Cache Handlers.
    """
    def __init__(self, cache):
        """
        Initialize our _cache variable for whichever cache we're using.

        :return: Nothing to return.
        :rtype: None
        """
        self._cache = cache

    def get(self, key):
        """
        The get method gets sub-classed and implemented by the child cache service object.

        :param str key: The key to retrieve from the cache.
        :return: Nothing to return.
        :rtype: None
        """
        pass

    def set(self, key, value, lifetime):
        """
        The set method gets sub-classed and implemented by the child cache service object.

        :param str key: The key to set in the cache.
        :param str value: The value to set in the cache.
        :param int lifetime: The lifetime of the key, value.
        :return: Nothing to return.
        :rtype: None
        """
        pass

    def delete(self, key):
        """
        The delete method gets sub-classed and implemented by the child cache service object.

        :param str key: The key to delete from the cache.
        :return: Nothing to return.
        :rtype: None
        """
        pass

    def get_stats(self):
        """
        The get_stats method gets sub-classed and implemented by the child cache service object.

        :return: Nothing to return.
        :rtype: None
        """
        pass

    def flush_all(self):
        """
        The flush_all method gets sub-classed and implemented by the child cache service object.

        :return: Nothing to return.
        :rtype: None
        """
        pass


class GenericCacheHandler(CacheHandler):
    """
    Generic cache handler that supports the basic subset of cache methods.
    """
    def get(self, key):
        """
        Get the cached data based off of the supplied key.

        :param str key: The key to fetch data for.
        :return: Return the cached data.
        :rtype: list
        """
        return self._cache.get(key)

    def set(self, key, value, lifetime):
        """
        Set the key, value, and lifetime in our generic cache.

        :param str key: The key to store.
        :param list value: The value to store.
        :param int lifetime: The expiry time for the data.
        :return: Returns True if the key setting was successful.
        :rtype: bool
        """
        return self._cache.set(key, value, lifetime)

    def delete(self, key):
        """
        Delete a specific key from the cache.

        :param str key: The key to delete from the cache.
        :return: Returns the number of keys deleted.
        :rtype: int
        """
        return self._cache.delete(key)

    def get_stats(self):
        """
        Get the generic stats using the get_stats function.

        :return: Returns a dictionary containing information regarding the stats of the cache.
        :rtype: dict
        """
        return self._cache.get_stats()

    def flush_all(self):
        """
        Delete all the keys and values from the Redis cache.

        :return: Returns the number of keys evicted from the cache.
        :rtype: int
        """
        return self._cache.flush_all()


class RedisCacheHandler(CacheHandler):
    """
    Redis cache handler that supports the basic subset of cache methods.
    """
    def get(self, key):
        """
        Get the cached data based off of the supplied key.

        :param str key: The key to fetch data for.
        :return: Return the cached data.
        :rtype: list
        """
        data = self._cache.get(key)
        if data:
            return cPickle.loads(data)
        return None

    def set(self, key, value, lifetime):
        """
        Set the key, value, and lifetime in our Redis cache. Use the cPickle Protocol version 2
        while dumping, as it is faster and produces better results with new-style classes.

        :param str key: The key to store.
        :param list value: The value to store.
        :param int lifetime: The expiry time for the data.
        :return: Returns True if the key setting was successful.
        :rtype: bool
        """
        return self._cache.setex(name=key, time=lifetime, value=cPickle.dumps(value, 2))

    def delete(self, key):
        """
        Delete a specific key from the cache.

        :param str key: The key to delete from the cache.
        :return: Returns the number of keys deleted.
        :rtype: int
        """
        return self._cache.delete(key)

    def get_stats(self):
        """
        Get the Redis stats using the info function.

        :return: Returns a dictionary containing information regarding the stats of the cache.
        :rtype: dict
        """
        return self._cache.info()

    def flush_all(self):
        """
        Delete all the keys and values from the Redis cache.

        :return: Returns the number of keys evicted from the cache.
        :rtype: int
        """
        keys = self._cache.keys('*')
        evicted_key_count = 0
        for i in xrange(0, len(keys), 1000):
            evicted_key_count += self._cache.delete(*keys[i:i+1000])
        return evicted_key_count
        
        
class CacheHandlerFactory():
    """
    Factory implementation that instantiates cache handlers based on config values.
    """
    def __init__(self, registry):
        """
        Initialize the `CacheHandlerFactory`.

        :param dict registry: The blimp registry dictionary containing all our configuration.
        :return: Nothing to return as it's just initialization.
        :rtype: None
        """
        self._registry = registry

    def _get_default_cache_handler(self):
        """
        Get the default cache handler name as per the configuration file.

        :return: Returns the default cache handler name.
        :rtype: str
        """
        cache_handler_name = self._registry['config'].get('cache.default.handler')
        if not cache_handler_name:
            raise Exception(500, 'No default cache handler configured in cache.default.handler')
        return cache_handler_name

    def get_cache_handler(self, cache_handler_name=None):
        """
        Get an instance of the cache handler.

        :param str cache_handler_name: The name of the cache handler to bootstrap.
        :return: Returns a cache handler object based on the cache handler name.
        :rtype: `GenericCacheHandler` || `RedisCacheHandler`
        :raises: Exception(500, 'Cache handler not found: <CacheName>')
        """
        if not cache_handler_name:
            cache_handler_name = self._get_default_cache_handler()

        if cache_handler_name == 'memcache':
            cache = memcache.Client(self._registry['config'].get('cache.memcache.servers'), debug=0)
            return GenericCacheHandler(cache)

        if cache_handler_name == 'redis':
            cache = redis.StrictRedis(host=self._registry['config'].get('redis.host'),
                                      port=self._registry['config'].getint('redis.port'),
                                      db=self._registry['config'].getint('cache.redis.db'))
            return RedisCacheHandler(cache)

        else:
            raise Exception(500, 'Cache handler not found: ' + cache_handler_name)
