puppy
=====

Puppy Cache - for preventing Dogpiles

How it works
============

Dogpiles happen when content which is cached on demand for user requests expires.  The next request will try to generate a fresh copy of the content.  If you only have one request in the time it takes to generate the content, there's no issue.

But on a busy site, you may have 50 requests find the cache expired.  And each one will try to update the content.  This causes a huge spike in server load, which can in turn slow down all the requests, including those trying to generate the content.  This can cascade, delaying the update and thus allowing more dogs to pile on as requests keep coming.

Puppy cache works by allowing you to keep serving "stale" content, whilst one - and only one - client generates the update.

This is done by having a "status" key in the cache which has the timeout.  Every time you get() a value, its status is checked.  If it's expired, the cache will try to lock the status key.  If it acquires the lock, it will generate new content and update.  Otherwise, it will serve the old, stale copy of the data.

Serving stale content isn't a problem, because you're already doing it.  Cached data are stale by definition.

To avoid data becoming too stale, the data key is set with an expirey time that is twice the update time longer than the status key's.

Install
=======

Install as a cache backend as you would any other:

    'BACKEND': 'puppy.cache.PuppyCache',

It currently requires Redis 2.6.12 or greater, as it uses the new combined SET command to affect SETNX and SETEX in one step.

Usage
=====

In all ways, it acts exactly as RedisCache, but provides a new method:

    cache.pget(key, callback, update_time=30):

Call this to retrieve a dogpile proof value.

If the value has expired, the callback is invoked and expected to set the new value, as well as return it.

When the status is locked for update, a shorter expirey time is used in case the task fails.  This time is the `update_time`.

The key's timeout will be set to (timeout + 2 * update_time)

