# -*- coding: utf-8 -*-
import os

MONGO_HOST = {
	'mac_pro': 'localhost'
}

SETTINGS_PATH = os.path.dirname(os.path.abspath(__file__))

KRAKEN_DIR = {
	'api': SETTINGS_PATH + '/kraken/api/',
	'stream': SETTINGS_PATH + '/kraken/stream/',
	'build': SETTINGS_PATH + '/kraken/build/',
	'save': SETTINGS_PATH + '/kraken/save/',
	'model': SETTINGS_PATH + '/kraken/model/'
}

POLONIEX_DIR = {
	'api': SETTINGS_PATH + '/api/',
	'stream': SETTINGS_PATH + '/stream/',
	'build': SETTINGS_PATH + '/build/',
	'save': SETTINGS_PATH + '/save/',
	'model': SETTINGS_PATH + '/model/'
}