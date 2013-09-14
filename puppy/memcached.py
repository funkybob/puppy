
'''
Puppy Cache

'''
from django.core.cache.backend.memcached import PyLibMCCache

from django.conf import settings

from time import sleep

import logging
log = logging.getLogger(__name__)

CURRENT = 'current'
UPDATING = 'updating'

SLEEP = getattr(settings, 'PUPPY_SLEEP', 0.1)

class PuppyCache(PyLibMCCache):

    def pget(self, key, callback, timeout=None, update_time=30):
        # Status key
        key = self.make_key(key)
        state_key = 'puppy:' + key

        # Get the value and its status
        value, status = self._client.get_multi([key, state_key])

        # If the status has expired, or we have no value
        while not status or value is None:
            # Try to gain an updating lock
            if self._client.add(state_key, UPDATING, self._get_memcache_timeout(update_time):
                try:
                    value = callback(key)
                except:
                    self._client.delete(state_key)
                    raise

                # Resolve our timeout value
                if timeout is None:
                    timeout = self.default_timeout
                toast_timeout = timeout + (update_time * 2)

                status = CURRENT
                self._client.set(key, value, self._get_memcache_timeout(toast_timeout))
                self._client.set(state_key, status, self._get_memcache_timeout(timeout))
            # Someone else is already updating it, but we don't have a value
            # to return, so we must wait
            elif not value:
                # Get fresh state/value
                value, status = self._client.get_multi([key, state_key])
                # We must wait as there is no "stale" value to return
                while status == UPDATING:
                    sleep(SLEEP)
                    value, status = self._client.get_multi([key, state_key])
            else:
                # We get here if no status, failed to lock, but we have a value
                # so it's safe to fall through and return the value
                break

        return value
