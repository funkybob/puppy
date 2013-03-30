
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
        value, status = pipe.get(key).get(state_key).execute()
        if value is not None:
            value = self.client.unpickle(value)

        # If the status has expired, or we have no value
        while not status or value is None:
            log.debug("[%s] No status", key)
            # Try to gain an updating lock
            # We need to pickle it ourselves here, as we bypass cache layers
            if redis.setnx(state_key, self.client.pickle(UPDATING)):
                redis.expire(state_key, update_time)
                log.debug("[%s] Invoking callback", key)
                try:
                    value = callback(key)
                except:
                    log.warning("[%s] Callback raised exception", key)
                    redis.delete(state_key)
                    raise

                # Resolve our timeout value
                if timeout is None:
                    timeout = self.default_timeout
                toast_timeout = timeout + (update_time * 2)

                log.debug("[%s] Setting value [%d]", key, toast_timeout)
                log.debug("[%s] Status: current", state_key)
                pipe.setex(key, self.client.pickle(value), int(toast_timeout))
                status = CURRENT
                pipe.setex(state_key, status, int(timeout))
                pipe.execute()
            # Someone else is already updating it
            elif not value:
                # We must wait as there is no "stale" value to return
                while True:
                    status, value = pipe.get(state_key).get(key).execute()
                    if status != UPDATING:
                        break
                    sleep(1)
                # If the status expired, the updating task raised an exception
                if status:
                    log.debug('[%s] Returning fresh value', key)
                    value = self.client.unpickle(value)
            # Fall through to returning the stale value
        else:
            log.debug("[%s] Returning cached value", key)

        return value
