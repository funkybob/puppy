
'''
Puppy Cache

'''
from redis_cache.cache import RedisCache

from time import sleep

import logging
log = logging.getLogger(__name__)

CURRENT = 'current'
UPDATING = 'updating'

class PuppyCache(RedisCache):

    def pget(self, key, callback, timeout=None, update_time=30):
        redis = self.raw_client
        pipe = redis.pipeline()

        # Status key
        key = self.make_key(key)
        state_key = 'puppy:' + key

        # Get the value and its status
        value, status = redis.mget(key, state_key)
        if value is not None:
            value = self.client.unpickle(value)

        # If the status has expired, or we have no value
        while not status or value is None:
            # Try to gain an updating lock
            if redis.setnx(state_key, UPDATING):
                redis.expire(state_key, update_time)
                try:
                    value = callback(key)
                except:
                    redis.delete(state_key)
                    raise

                # Resolve our timeout value
                if timeout is None:
                    timeout = self.default_timeout
                toast_timeout = timeout + (update_time * 2)

                status = CURRENT
                pipe.setex(key, self.client.pickle(value), int(toast_timeout)).setex(state_key, status, int(timeout))
                pipe.execute()
            # Someone else is already updating it
            elif not value:
                # We must wait as there is no "stale" value to return
                while status != UPDATING:
                    sleep(0.1)
                    status, value = redis.mget(state_key, key)
                # If the status expired, the updating task raised an exception
                if status:
                    if value is not None:
                        value = self.client.unpickle(value)
            # Fall through to returning the stale value

        return value
