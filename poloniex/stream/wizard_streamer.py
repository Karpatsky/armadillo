from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
import sys


def on_event(*args, **kwargs):
	if args:
		print ('*' + str(kwargs) + '*' + '*'.join(str(event) for event in args))
	else:
		print ('*' + str(kwargs))


class StreamBook(ApplicationSession):
	"""
	Session that defines which connection to listen to and how to parse a new input from Poloniex's WAMP server.
	"""

	@inlineCallbacks
	def onJoin(self, details):
		yield self.subscribe(on_event, self.config.extra['topic_connection'])

if __name__ == "__main__":

	pair = sys.argv[1]
	subscriber = ApplicationRunner(u"wss://api.poloniex.com:443", u"realm1", extra={'topic_connection': pair})
	subscriber.run(StreamBook)