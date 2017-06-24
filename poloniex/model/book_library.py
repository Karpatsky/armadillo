from __future__ import print_function
from bson.binary import Binary
import cPickle
from arctic import Arctic, register_library_type
from arctic.decorators import mongo_retry


class BookData(object):
	"""
	This BookData class is the main data model for book data that has already been constructed by our scripts.
	An instance of BookData contains a timestamp and the corresponding updated bid, ask, and/or trade book.
	This model for data storage is implemented by BookDataLibrary, our custom Arctic library implementation of MongoDB.
	"""

	def __init__(self, timestamp, bid_book=None, ask_book=None, trade_book=None):
		self.timestamp = timestamp
		if bid_book:
			self.bid_book = {'rate_tree': bid_book['rate_tree'],
			                 'rate_dict': bid_book['rate_dict']
			                 }
		else:
			self.bid_book = None
		if ask_book:
			self.ask_book = ask_book
			self.ask_book = {'rate_tree': ask_book['rate_tree'],
			                 'rate_dict': ask_book['rate_dict']
			                 }
		else:
			self.ask_book = None
		if trade_book:
			self.trade_book = trade_book
			self.trade_book = {'trade_deque': trade_book['trade_deque'],
			                 'trade_dict': trade_book['trade_dict']
			                 }


class BookDataLibrary(object):
	"""
	This BookLibrary class is a custom implementation of the Arctic MongoDB layer optimized for sharding, storing,
	indexing, and querying cryptocurrency book data constructed by our book builders.
	"""
	_LIBRARY_TYPE = 'wg-crypto.BookDataLibrary'

	def __init__(self, arctic_lib):
		self._arctic_lib = arctic_lib
		# arctic_lib automatically provides a root pymongo.Collection to store data
		self._collection = arctic_lib.get_top_level_collection()
		# Data can also be stored in specific sub_collections created by you
		self._sub_collection = self._collection.sub_collection
		# Fetch some per-library metadata for this library
		self.some_metadata = arctic_lib.get_library_metadata('some_metadata')  # MUST EDIT

	@classmethod
	def initialize_library(clscls, arctic_lib, **kwargs):
		# Persist some per-library metadata in this arctic_lib
		arctic_lib.set_library_metadata('some_metadata', 'some_value')  # MUST EDIT
		BookDataLibrary(arctic_lib)._ensure_index()

	def _ensure_index(self):
		"""
		Index the fields that get used by queries
		"""
		collection = self._collection
		collection.create_index('timestamp')  # MUST EDIT

	@mongo_retry
	def query(self, *args, **kwargs):
		"""
		Generic query method that creates a generator to yield data that matches the query.
		A Generator is the most memory efficient choice here, as the entire set of documents that match the query isn't
		handled in memory at once.
		"""
		for book_tick in self._collection.find(*args, **kwargs):
			book_tick['bid_book'] = cPickle.loads(book_tick['bid_book'])
			book_tick['ask_book'] = cPickle.loads(book_tick['ask_book'])
			book_tick['trade_book'] = cPickle.loads(book_tick['trade_book'])
			del book_tick['_id']
			yield BookData(book_tick)

	@mongo_retry
	def stats(self):
		"""
		Database usage statistics.
		Used by quota.
		"""
		stats = {}
		db = self._collection.database
		stats['dbstats'] = db.command('dbstats')
		stats['data'] = db.command('collstats', self._collection.name)
		stats['totals'] = {'count': stats['data']['count'], 'size': stats['data']['size']}
		return stats

	@mongo_retry
	def store(self, book_data):
		"""
		Simple persistence method
		"""
		to_store = {'pair': book_data.pair, 'timestamp': book_data.timestamp,
					'bid_book': Binary(cPickle.dumps(book_data.bid_book)),
					'ask_book': Binary(cPickle.dumps(book_data.ask_book)),
					'trade_book': Binary(cPickle.dumps(book_data.trade_book))}

		# Respect any soft-quota on write - raises if stats().totals.size > quota
		self._arctic_lib.check_quota()
		self._collection.insert_one(to_store)

	@mongo_retry
	def delete(self, query):
		"""
		Simple delete method
		"""
		self._collection.delete_one(query)

