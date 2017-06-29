from poloniex.settings import POLONIEX_DIR
from poloniex.api.api import PoloniexAPI
from poloniex.model.wizard_build import Tick, BidBook, AskBook, TradeBook

from wizard import Wizard
import time

class MarketMaker(object):

	def __init__(self, wizard):
		print("initializing market maker...")
		self.wizard = wizard

	def start(self):
		print("starting market maker...")
		self.wizard.start_book()
		#while True:
			#self.calculate_spread()
			#time.sleep(.5)

	def calculate_spread(self):
		max_bid_level = self.get_bids().max_rate_level()
		max_ask_level = self.get_asks().max_rate_level()
		print("max bid level is " + str(max_bid_level))
		spread = max_ask_level[0] - max_bid_level[0]
		print("Spread is " + str(spread))

	def get_bids(self):
		return self.wizard.bid_book

	def get_asks(self):
		return self.wizard.ask_book