# from twisted.internet.defer import inlineCallbacks
# from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
# import json
# import sys
#
# def on_event(*args, **kwargs): # everytime we get a push message from the polo ticker
# 	print('X[' + str(kwargs) + ']X' + json.dumps(args)) #split on X for message
#
# class StreamBook(ApplicationSession):
# 	"""
# 	Subscribes to a specific WAMP connection in the Poloniex API.
# 	"""
#
# 	@inlineCallbacks
# 	def onJoin(self, details):
# 		#print self.config.extra['v1']
# 		yield self.subscribe(on_event, 'BTC_ETC')
#
#
#
# if __name__ == "__main__":
# 	# parser = argparse.ArgumentParser()
# 	# parser.add_argument('pair')
# 	# arg = parser.parse_args()
# 	# arg = sys.argv[1]
# 	#subscriber = ApplicationRunner(u"wss://api.poloniex.com:443", u"realm1", extra={'v1': 'BTC_ETH', 'v2': 'BTC_ETH'})
# 	subscriber = ApplicationRunner(u"wss://api.poloniex.com:443", u"realm1")
# 	# if arg == 'BTC_ETH':
# 	# 	subscriber.run(StreamBookBTCETH)
# 	# if arg == 'BTC_ETC':
# 	# 	subscriber.run(StreamBookBTCETC)
# 	# if arg == 'BTC_ETH':
# 	# 	subscriber.run(StreamBookBTCETH)
# 	subscriber.run(StreamBook)
# 	# print subscriber.extra
