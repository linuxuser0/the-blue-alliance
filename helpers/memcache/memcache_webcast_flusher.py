import logging

from google.appengine.api import memcache


from controllers.ajax_controller import WebcastHandler
from controllers.event_controller import EventList
from controllers.main_controller import MainCompetitionseasonHandler, MainOffseasonHandler, MainInsightsHandler, GamedayHandler, WebcastsHandler


class MemcacheWebcastFlusher(object):
    @classmethod
    def flush(self):
        flushed = []

        flushed.append(MainCompetitionseasonHandler().memcacheFlush())
        flushed.append(MainOffseasonHandler().memcacheFlush())
        flushed.append(MainInsightsHandler().memcacheFlush())
        flushed.append(GamedayHandler().memcacheFlush())
        flushed.append(WebcastsHandler().memcacheFlush())
        flushed.append(EventList().memcacheFlush())

        return flushed

    @classmethod
    def flushEvent(self, event_key):
        flushed = self.flush()
        flushed.append(WebcastHandler().memcacheFlush(event_key))
        return flushed
