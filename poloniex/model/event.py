import collections


class Event(collections.MutableMapping):
	"""
	An Event represents a single order data event.
	This class inherits from a dictionary.
	"""

	def __init__(self, *args, **kwargs):
		self.store = dict()
		self.update(dict(*args, **kwargs))  # use the free update to set keys

	def __getitem__(self, key):
		return self.store[self.__keytransform__(key)]

	def __setitem__(self, key, value):
		self.store[self.__keytransform__(key)] = value

	def __delitem__(self, key):
		del self.store[self.__keytransform__(key)]

	def __iter__(self):
		return iter(self.store)

	def __len__(self):
		return len(self.store)

	def __keytransform__(self, key):
		return key


class Event(object):
	"""
	An Event represents a single order data event.
	"""

	def __init__(self, event):
		"""
		Initializes an event object, which is made of a stream type, order type, price and, optionally, volume.

		Args:
			event: String representing event found within the tick string from the STDOUT of exchange API.

		"""
		event = ast.literal_eval(event)

		# str: Type of stream event, can be "orderBookModify", "orderBookRemove" or "newTrade"
		self.stream_type = event[u'type'].encode('ascii', 'ignore')

		# str: Type of order event, can be "bid", "ask", "buy", or "sell"
		self.order_type = event[u'data'][u'type'].encode('ascii', 'ignore')

		# float: rate associated with event
		self.rate = float(event[u'data'][u'rate'])

		# float: amount associated with event, in units of the second member of the pair
		# for ex., if pair = 'BTC_ETH', then u'amount' corresponds with amount of ETH in trade
		# value implied as total volume at price level if an "OrderBookRemove"
		if self.stream_type != "orderBookRemove":
			self.amount = float(event[u'data'][u'amount'])
		else:
			self.amount = np.nan

	def __str__(self):

		return str(self.__dict__)

	def to_dict(self):
		return self.__dict__