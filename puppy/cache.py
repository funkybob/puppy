
'''
Puppy Cache

'''
from redis_cache.cache import RedisCache

from django.conf import settings

from time import sleep

import logging
log = logging.getLogger(__name__)

CURRENT = 'current'
UPDATING = 'updating'

SLEEP = getattr(settings, 'PUPPY_SLEEP', 0.1)

class PuppyCache(RedisCache):

    def pget(self, key, callback, timeout=None, update_time=30):
        redis = self.raw_client
        pipe = redis.pipeline(transaction=False)

        # Status key
        key = self.make_key(key)
        state_key = 'puppy:' + key

        # Get the value and its status
        value, status = redis.mget(key, state_key)

        # If the status has expired, or we have no value
        while not status or value is None:
            # Try to gain an updating lock
            if redis.set(state_key, UPDATING, ex=update_time, nx=True):
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
                # Even if the value is None, pickled None is not None
                value = self.client.pickle(value)
                pipe.setex(
                    key, value, int(toast_timeout)
                ).setex(
                    state_key, status, int(timeout)
                ).execute()
            # Someone else is already updating it, but we don't have a value
            # to return, so we must wait
            elif not value:
                # Get fresh state/value
                value, status = redis.mget(key, state_key)
                # We must wait as there is no "stale" value to return
                while status == UPDATING:
                    sleep(SLEEP)
                    value, status = redis.mget(key, state_key)
            else:
                # We get here if no status, failed to lock, but we have a value
                # so it's safe to fall through and return the value
                break

        if value is not None:
            value = self.client.unpickle(value)

        return value
