
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

    def make_state_key(self, key):
        return self.make_key('puppy:' + key)

    def pget(self, key, callback, timeout=None, update_time=30):
        client = self._client

        # Status key
        state_key = self.make_state_key(key)

        # Get the value and its status
        value = self.get(key)
        status = self.get(state_key)

        # If the status has expired, or we have no value
        if not status or not value:
            log.debug("[%s] No status", key)
            # Try to gain an updating lock
            if client.setnx(state_key, self.pickle(UPDATING)):
                client.expire(state_key, update_time)
                log.debug("[%s] Invoking callback", key)
                value = callback(key)
                self.pset(key, value, timeout=None, update_time=update_time)
            # Someone else is already updating it
            elif value is None:
                # We must wait as there is no "stale" value to return
                while True:
                    status = self.get(state_key)
                    if status != UPDATING:
                        break
                    sleep(1)
                log.debug('[%s] Returning fresh value', key)
                value = self.get(key)
            # Fall through to returning the stale value

        log.debug("[%s] Returning cached value", key)
        return value

    def pset(self, key, value, timeout=None, update_time=30):
        '''Set this key, and mark its puppy key current'''
        state_key = self.make_state_key(key)

        # Calculate too-stale-for-toast timeout
        if timeout is None:
            timeout = self.default_timeout
        toast_timeout = timeout + (update_time * 2)

        log.debug("[%s] Setting value [%d]", key, toast_timeout)
        self.set(key, value, timeout=toast_timeout)
        log.debug("[%s] Status: current", state_key)
        self.set(state_key, self.pickle(CURRENT), timeout=timeout)

        return value
