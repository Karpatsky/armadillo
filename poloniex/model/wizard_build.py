from bintrees import FastRBTree
from collections import deque
import datetime
import dateutil.parser
import ast


class Tick(object):
	"""
	A Tick represents a line of order data activity for a specific timestamp.
	A Tick is comprised of many Events.
	"""

	def __init__(self, tick):
		"""
		Initializes a tick object, which is comprised of a timestamp, sequence and many events

		Args:
			tick: String representing tick received from STDOUT of exchange API.

		"""

		self.timestamp = datetime.datetime.utcnow()
		self.bid_arr = []
		self.ask_arr = []
		self.trade_arr = []

		for i, event_str in enumerate(tick.split('*')):
			# ignoring i=0 because it contains timestamp sent from poloniex, which lacks too much accuracy to be useful
			# sequence is always second in tick
			if i == 1:
				self.sequence = ast.literal_eval(event_str)[u'seq']
			elif i > 1:
				event = ast.literal_eval(event_str)
				# stream_type and order_type used to make separate lists for modifying tradeDeque, bidTree and askTree
				if event[u'type']== "newTrade":
					self.trade_arr.append(event)

				if event[u'data'][u'type'] == "bid":
					self.bid_arr.append(event)

				elif event[u'data'][u'type'] == "ask":
					self.ask_arr.append(event)

	def __str__(self):
		ret_str = "TICK - Timestamp: {0}, Sequence: {1}, Bids: {2}, 'Asks: {3}, Trades: {4}"
		return ret_str.format(self.timestamp, self.sequence, self.bid_arr, self.ask_arr, self.trade_arr)


class BidBook(object):
	"""
	A BidBook is used to store the order book's rates and amounts on the bid side with a defined depth.
	To maintain a sorted order of rates, the BidBook uses a red-black tree to store rates and corresponding amounts.
	For O(1) query of volume at a predetermined rate, the BidBook also uses a dictionary to store rate and amount.
	"""

	def __init__(self, max_depth, data):
		# RBTree: maintains sorted order of rates
		# every value inserted to RBTree must be a tuple, so we hard code the second value to be 0
		self.rate_tree = FastRBTree()

		# dict: Uses rate and amount for key value pairs
		self.rate_dict = {}

		# float: amounts summed across all rate levels in tree
		self.volume = 0

		# int: total number of rate levels in tree
		self.depth = len(data)

		# int: maximum number of rate levels in tree
		self.max_depth = max_depth

		# populate rate_tree and rate_dict from public API call data
		# set volume
		for level in data:
			rate = float(level[0])
			amount = float(level[1])
			self.rate_tree.insert(rate, 0)
			self.rate_dict[rate] = amount
			self.volume += amount

	def __len__(self):
		return len(self.rate_dict)

	def rate_exists(self, rate):
		return rate in self.rate_dict

	def get_amount_at_rate(self, rate):
		return self.rate_dict.get(rate)

	def max_rate_level(self):
		if self.depth > 0:
			rate = self.rate_tree.max_key()
			amount = self.get_amount_at_rate(rate)
			return rate, amount
		else:
			return None

	def min_rate_level(self):
		if self.depth > 0:
			rate = self.rate_tree.min_key()
			amount = self.get_amount_at_rate(rate)
			return rate, amount
		else:
			return None

	def modify(self, event):
		# if the event's rate is already in the book, just modify the amount at the event's rate
		rate = float(event[u'data'][u'rate'])
		amount = float(event[u'data'][u'amount'])
		if self.rate_exists(rate):
			# print '~~~~~~~~~~~~~~~~~~~~~~  BID MODIFY  ~~~~~~~~~~~~~~~~~~~~~~'
			self.rate_dict[rate] = amount

		# only rates not already in the book reach this logic
		# if the max depth hasn't been reached, just insert the event's rate and amount
		elif self.depth < self.max_depth:
			# print '~~~~~~~~~~~~~~~~~~~~~~  BID MODIFY  ~~~~~~~~~~~~~~~~~~~~~~'
			self.rate_tree.insert(rate, 0)
			self.rate_dict[rate] = amount
			self.depth += 1

		# only events being handled by a full order tree reach this logic
		# if the event is a bid and the rate is greater than min rate, effectively replace min rate level with event
		else:
			min_rate = self.min_rate_level()[0]
			if rate > min_rate:
				# print '~~~~~~~~~~~~~~~~~~~~~~  BID MODIFY  ~~~~~~~~~~~~~~~~~~~~~~'
				self.rate_tree.remove(min_rate)
				del self.rate_dict[min_rate]
				self.rate_tree.insert(rate, 0)
				self.rate_dict[rate] = amount

	def remove(self, event):
		# if the event's rate is in the book, delete it
		rate = float(event[u'data'][u'rate'])
		if self.rate_exists(rate):
			# print '~~~~~~~~~~~~~~~~~~~~~~  BID REMOVE  ~~~~~~~~~~~~~~~~~~~~~~'
			self.rate_tree.remove(rate)
			del self.rate_dict[rate]
			self.depth -= 1

	def __str__(self):
		rate_tree_str = '[' + ','.join(rate[0] for rate in self.rate_tree) + ']'
		return 'BIDS: ' + rate_tree_str


class AskBook(object):
	"""
	An AskBook is used to store the order book's rate and volume on the ask side with a max depth.
	To maintain a sorted order of rates, the AskBook uses a red-black tree to store rates.
	For O(1) query of volume at a predetermined rate, the AskBook uses a dictionary to store rate and volume.
	"""

	def __init__(self, max_depth, data):
		# RBTree: maintains sorted order of rates
		self.rate_tree = FastRBTree()

		# dict: Uses rate and volume for key value pairs
		self.rate_dict = {}

		# float: amounts summed across all rate levels in tree
		self.volume = 0

		# int: total number of rate levels in tree
		self.depth = len(data)

		# int: maximum number of rate levels in tree
		self.max_depth = max_depth

		# populate rate_tree and rate_dict from public API call data
		# set volume
		for level in data:
			rate = float(level[0])
			amount = float(level[1])
			self.rate_tree.insert(rate, 0)
			self.rate_dict[rate] = amount
			self.volume += amount

	def __len__(self):
		return len(self.rate_dict)

	def rate_exists(self, rate):
		return rate in self.rate_dict

	def get_amount_at_rate(self, rate):
		return self.rate_dict.get(rate)

	def max_rate_level(self):
		if self.depth > 0:
			rate = self.rate_tree.max_key()
			amount = self.get_amount_at_rate(rate)
			return rate, amount
		else:
			return None

	def min_rate_level(self):
		if self.depth > 0:
			rate = self.rate_tree.min_key()
			amount = self.get_amount_at_rate(rate)
			return rate, amount
		else:
			return None

	def modify(self, event):
		rate = float(event[u'data'][u'rate'])
		amount = float(event[u'data'][u'amount'])
		# if the event's rate is already in the book, just modify the volume at the event's rate
		if self.rate_exists(rate):
			# print '~~~~~~~~~~~~~~~~~~~~~~  ASK MODIFY  ~~~~~~~~~~~~~~~~~~~~~~'
			self.rate_dict[rate] = amount

		# only rates not already in the book reach this logic
		# if the max depth hasn't been reached, just insert the event's rate and volume
		elif self.depth < self.max_depth:
			# print '~~~~~~~~~~~~~~~~~~~~~~  ASK MODIFY  ~~~~~~~~~~~~~~~~~~~~~~'
			self.rate_tree.insert(rate, 0)
			self.rate_dict[rate] = amount
			self.depth += 1

		# only events being handled by a full order tree reach this logic
		# if the event is an ask and the rate is less than max rate, effectively replace min rate level with event
		else:
			max_rate = self.max_rate_level()[0]
			if rate < max_rate:
				# print '~~~~~~~~~~~~~~~~~~~~~~  ASK MODIFY  ~~~~~~~~~~~~~~~~~~~~~~'
				self.rate_tree.remove(max_rate)
				del self.rate_dict[max_rate]
				self.rate_tree.insert(rate, 0)
				self.rate_dict[rate] = amount

	def remove(self, event):
		# if the event's rate is in the book, delete it
		rate = float(event[u'data'][u'rate'])
		if self.rate_exists(rate):
			# print '~~~~~~~~~~~~~~~~~~~~~~  ASK REMOVE  ~~~~~~~~~~~~~~~~~~~~~~'
			self.rate_tree.remove(rate)
			del self.rate_dict[rate]
			self.depth -= 1

	def __str__(self):
		rate_tree_str = '[' + ','.join(rate[0] for rate in reversed(self.rate_tree)) + ']'
		return 'ASKS: ' + rate_tree_str


class TradeBook(object):
	"""
	A TradeBook is used to store the most recent completed trades with a max depth.
	A trade_deque is used to chronologically store tradeIDs, makes removing old trades and adding new trades O(1).
	The trade_deque goes oldest to newest from left to right.
	A trade_dict is used to support querying from rates in the tree to the corresponding indexes in the deque.
	"""

	def __init__(self, max_depth, data):
		# deque: maintains chronological order of trades
		self.trade_deque = deque(maxlen=max_depth)

		# dict: Uses tradeID and data for key value pairs
		self.trade_dict = {}

		# populate trade_deque and trade_dict from public API call data
		# set volume
		for trade in (reversed(data[0:max_depth])):
			# global_trade_id = trade[u'globalTradeID'].encode('ascii', 'ignore')
			trade_id = trade[u'tradeID']
			timestamp = dateutil.parser.parse(trade[u'date'].encode('ascii', 'ignore'))
			rate = float(trade[u'rate'])
			# key u'amount' contains volume of second member of pair
			# for ex., if pair = 'BTC_ETH', then u'amount' corresponds with amount of ETH in trade
			amount = float(trade[u'amount'])
			total = float(trade[u'total'])
			trade_type = trade[u'type'].encode('ascii', 'ignore')

			self.trade_deque.append(trade_id)
			self.trade_dict[trade_id] = {'timestamp': timestamp, 'rate': rate, 'amount': amount, 'total': total, 'type': trade_type}

	def __len__(self):
		return len(self.trade_dict)

	def trade_exists(self, trade_id):
		return trade_id in self.trade_dict

	def get_trade_at_id(self, trade_id):
		return self.trade_dict.get(trade_id)

	def new_trade(self, event):
		timestamp = datetime.datetime.utcnow()
		trade_id = event[u'data'][u'tradeID']
		rate = float(event[u'data'][u'rate'])
		amount = float(event[u'data'][u'amount'])
		total = float(event[u'data'][u'total'])
		trade_type = event[u'data'][u'rate'].encode('ascii', 'ignore')
		if len(self) < self.trade_deque.maxlen:
			# print '~~~~~~~~~~~~~~~~~~~~~~~~  TRADE  ~~~~~~~~~~~~~~~~~~~~~~~~'
			self.trade_deque.append(trade_id)
			self.trade_dict[trade_id] =  {'timestamp': timestamp, 'rate': rate, 'amount': amount, 'total': total, 'type': trade_type}
		elif len(self) == self.trade_deque.maxlen:
			# print '~~~~~~~~~~~~~~~~~~~~~~  TRADE  ~~~~~~~~~~~~~~~~~~~~~~'
			oldest_id = self.trade_deque.popleft()
			del self.trade_dict[oldest_id]
			self.trade_deque.append(trade_id)
			self.trade_dict[trade_id] = {'timestamp': timestamp, 'rate': rate, 'amount': amount, 'total': total, 'type': trade_type}

	def __str__(self):
		deque_str = '[' + ','.join(trade for trade in self.trade_deque) + ']'
		return 'TRADES: ' + deque_str