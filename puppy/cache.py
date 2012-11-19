
'''
Puppy Cache

'''
from redis_cache.cache import RedisCache

from time import sleep

import logging
log = logging.getLogger(__name__)

class PuppyCache(RedisCache):

    def pget(self, key, callback, update_time=30):
        client = self._client

        # Status key
        state_key = 'puppy:' + key

        # Get the value and its status
        value = self.get(key)
        status = self.get(state_key)

        wait = not value

        # If the status has expired, or we have no value
        if not status or not value:
            log.debug("[%s] No status", key)
            # Try to gain an updating lock
            if client.setnx(state_key, 'updating'):
                client.expire(state_key, update_time)
                log.debug("[%s] Invoking callback", key)
                return callback(key)
            # Someone else is already updating it
            else:
                # We must wait as there is no "stale" value to return
                while(wait):
                    status = self.get(state_key)
                    if status != 'updating':
                        break
                    sleep(0.1)
                log.debug('[%s] Returning fresh value', key)
                return self.get(key)

        log.debug("[%s] Returning cached value", key)
        return value

    def pset(self, key, value, timeout=None, update_time=30):
        '''Set this key, and mark its puppy key current'''
        state_key = 'puppy:' + key

        # Calculate too-stale-for-toast timeout
        if timeout is None:
            timeout = self.default_timeout
        toast_timeout = timeout + (update_time * 2)

        log.debug("[%s] Setting value [%d]", key, toast_timeout)
        self.set(key, value, timeout=toast_timeout)
        log.debug("[%s] Status: current", state_key)
        self.set(state_key, 'current', timeout=timeout)

        return value
