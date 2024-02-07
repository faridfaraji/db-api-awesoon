from functools import wraps
from flask import request
from awesoon.core.cache import RedisClusterJson


redis_cluster = RedisClusterJson()


def cached(func):
    """Cache endpoints"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.method == "GET" and request.args:
            if request.url in redis_cluster:
                return redis_cluster.get(request.url), 200
            else:
                result, status = func(*args, **kwargs)
                if status == 200:
                    redis_cluster[request.url] = result
                return result, status
        else:
            return func(*args, **kwargs)
    return wrapper
