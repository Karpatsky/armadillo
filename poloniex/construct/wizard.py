
from poloniex.settings import POLONIEX_DIR
from poloniex.api.api import PoloniexAPI
from poloniex.model.wizard_build import Tick, BidBook, AskBook, TradeBook

from multiprocessing.dummy import Process as Thread
from subprocess import Popen, PIPE
import time


class Wizard(object):
	"""
	BookBuilder object used for controlling the order data thread and subprocess
	Holds poloniex ticker dict under self.markets
	"""

	def __init__(self, pair, depth):
		self.pair = pair
		print('BOOK: Starting book for pair: {0}'.format(self.pair))
		market_orders = PoloniexAPI().marketOrders(self.pair, depth)
		self.bid_book = BidBook(depth, market_orders['bids'])
		print('BOOK: bid_book populated with public API marketOrders() call')
		self.ask_book = AskBook(depth, market_orders['asks'])
		print('BOOK: ask_book populated with public API marketOrders() call')
		market_trade_history = PoloniexAPI().marketTradeHist(self.pair)
		self.trade_book = TradeBook(depth, market_trade_history)
		print('BOOK: trade_book populated with public API marketTradeHist() call')
		self._tickerP = Popen(["python", POLONIEX_DIR['stream'] + 'wizard_streamer.py', self.pair], stdout=PIPE, bufsize=1)
		print('BOOK: polo_streamer.py subprocess started')

	def start_book(self, pair, depth):
		"""
		Starts the ticker subprocess
		"""
		self._tickerT = Thread(target=self.catch_book)
		self._tickerT.daemon = True
		self._tickerT.start()
		print('BOOK: catch_book thread started')

	def stop_book(self):
		"""
		Stops the ticker subprocess
		"""
		self._tickerP.terminate()
		self._tickerP.kill()
		print('BOOK: polo_streamer.py subprocess stopped')
		self._tickerT.join()
		print('BOOK: catch_book thread joined')

	def catch_book(self):
		with self._tickerP.stdout:
			for tick_str in iter(self._tickerP.stdout.readline, b''):
				try:
					tick = Tick(tick_str)
					# print tick
					for bid in tick.bid_arr:
						if bid[u'type'] == 'orderBookRemove':
							self.bid_book.remove(bid)
						else:
							self.bid_book.modify(bid)

					for ask in tick.ask_arr:
						if ask[u'type'] == 'orderBookRemove':
							self.ask_book.remove(ask)
						else:
							self.bid_book.remove(ask)

					for trade in tick.trade_arr:
						self.trade_book.new_trade(trade)

					# print 'BID TREE: ' + str(self.bid_book.rate_tree)
					# print 'ASK TREE: ' + str(self.ask_book.rate_tree)
					# print 'TRADE DEQUE: ' + str(self.trade_book.trade_deque)

				except Exception as e:
					print(e)

		self._tickerP.wait()

# if __name__ == "__main__":
# 	test_popen = Popen(["python", POLONIEX_DIR['stream'] + 'wizard_streamer.py', 'BTC_ETH'], stdout=PIPE, bufsize=1)
# 	with test_popen.stdout:
# 			for tick_str in iter(test_popen.stdout.readline, b''):
# 				print(tick_str)

#if __name__ == "__main__":
	#btc_eth = Wizard('BTC_ETH', 10)
	#btc_etc = Wizard('BTC_ETC', 10)
	#eth_etc = Wizard('ETH_ETC', 10)

	#while True:
		#first_leg = btc_eth.ask_book.min_rate_level()[0]
		# print 'FIRST LEG: ' + str(first_leg)
		#second_leg = btc_etc.ask_book.min_rate_level()[0]
		# print 'SECOND LEG: ' + str(second_leg)
		#third_leg = eth_etc.bid_book.max_rate_level()[0]
		# print 'THIRD LEG: ' + str(third_leg)
		# print (first_leg * third_leg / second_leg) * (.9975 * .9975 * .9975)
		#inverse_first_leg = eth_etc.ask_book.min_rate_level()[0]
		# print 'INVERSE FIRST LEG: ' + str(inverse_first_leg)
		#inverse_second_leg = btc_etc.bid_book.max_rate_level()[0]
		# print 'INVERSE SECOND LEG: ' + str(inverse_second_leg)
		#inverse_third_leg = btc_eth.bid_book.max_rate_level()[0]
		# print 'INVERSE THIRD LEG: ' + str(inverse_third_leg)
		#print ("BTC-ETH MIN ASK: " + str(first_leg))
		#print ("BTC-ETC MIN ASK: " + str(second_leg))
		# print ("BTC-ETH MIN ASK: " + str(first_leg))
		# print (inverse_first_leg * inverse_third_leg / inverse_second_leg) * (.9975 * .9975 * .9975)
		#time.sleep(.5)
