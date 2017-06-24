from poloniex.settings import MONGO_HOST

from arctic import Arctic


if __name__ == "__main__":
	store = Arctic(MONGO_HOST['mac_pro'], app_name='wg-crypto')
	store.initialize_library('')