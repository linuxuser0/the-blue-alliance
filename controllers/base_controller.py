import webapp2

from time import mktime
from wsgiref.handlers import format_date_time

from google.appengine.api import memcache

import tba_config

from helpers.user_bundle import UserBundle
from models.user import User


class CacheableHandler(webapp2.RequestHandler):
    """
    Provides a standard way of caching the output of pages.
    Currently only supports logged-out pages.
    """

    def __init__(self, *args, **kw):
        super(CacheableHandler, self).__init__(*args, **kw)
        self._cache_expiration = 0
        self._cache_key = ""
        self._cache_version = 0

    @property
    def cache_key(self):
        return "{}:{}:{}".format(
            self._cache_key,
            self._cache_version,
            tba_config.CONFIG["static_resource_version"])

    def get(self, *args, **kw):
        cached_response = self._read_cache()
        if cached_response:
            self.response.headers = cached_response.headers
            self.response.out.write(cached_response.body)
        else:
            self.response.out.write(self._render(*args, **kw))
            self._write_cache(self.response)

    def _has_been_modified_since(self, datetime):
        last_modified = format_date_time(mktime(datetime.timetuple()))
        if_modified_since = self.request.headers.get('If-Modified-Since')
        if if_modified_since and if_modified_since == last_modified:
            self.response.set_status(304)
            return False
        else:
            self.response.headers['Last-Modified'] = last_modified
            return True

    def memcacheFlush(self):
        memcache.delete(self.cache_key)
        return self.cache_key

    def _read_cache(self):
        return memcache.get(self.cache_key)

    def _render(self):
        raise NotImplementedError("No _render method.")

    def _write_cache(self, response):
        if tba_config.CONFIG["memcache"]:
            memcache.set(self.cache_key, response, self._cache_expiration)


class LoggedInHandler(webapp2.RequestHandler):
    """
    Provides a base set of functionality for pages that need logins.
    Currently does not support caching as easily as CacheableHandler.
    """

    def __init__(self, *args, **kw):
        super(LoggedInHandler, self).__init__(*args, **kw)
        self.user_bundle = UserBundle()
        self.template_values = {
            "user_bundle": self.user_bundle
        }

    def _require_admin(self):
        self._require_login()
        if not self.user_bundle.is_current_user_admin:
            return self.redirect(self.user_bundle.login_url, abort=True)

    def _require_login(self, target_url="/"):
        if not self.user_bundle.user:
            return self.redirect(
                self.user_bundle.create_login_url(target_url),
                abort=True
            )
