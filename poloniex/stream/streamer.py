# from twisted.internet.defer import inlineCallbacks
# from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
# import json
# import sys
#
#
# def on_event(*args, **kwargs):
# 	print('X[' + str(kwargs) + ']X' + json.dumps(args))
#
#
# class Stream(ApplicationSession):
# 	"""
# 	Stream listens to a specific Poloniex WAMP server  and uses the on_event function to parse new input.
# 	"""
#
# 	@inlineCallbacks
# 	def onJoin(self, details):
# 		yield self.subscribe(on_event, self.config.extra['topic_connection'])
#
#
# if __name__ == "__main__":
#
# 	pair = sys.argv[1]
# 	subscriber = ApplicationRunner(u"wss://api.poloniex.com:443", u"realm1", extra={'topic_connection': pair})
# 	subscriber.run(Stream)