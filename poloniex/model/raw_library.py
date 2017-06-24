from __future__ import print_function
from bson.binary import Binary
import cPickle
from arctic import Arctic, register_library_type
from arctic.decorators import mongo_retry


class RawData(object):
	"""
	This RawData class is the main data model for raw data taken from the public API or WAMP server.
	An instance of RawData holds a data type and the contents of the corresponding public API call or WAMP stream tick.
	This model for data storage is implemented by RawDataLibrary, our custom Arctic library implementation of MongoDB.
	"""

	def __init__(self, data_type, data):
		self.data_type = data_type
		self.data = data