from wizard import Wizard
from mm_strat import MarketMaker

eth_wizard = Wizard('USDT_ETH', 10)

strategy = MarketMaker(eth_wizard)
strategy.start()