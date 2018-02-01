# pylint: disable=C0111,R0903
# -*- coding: utf-8 -*-

"""Displays the price of a cryptocurrency.

Requires the following python packages:
    * requests

Parameters:
    * getcrypto.interval: Interval in seconds for updating the price, default is 120, less than that will probably get your IP banned.
    * getcrypto.getbtc: 0 for not getting price of BTC, 1 for getting it (default).
    * getcrypto.geteth: 0 for not getting price of ETH, 1 for getting it (default).
    * getcrypto.getltc: 0 for not getting price of LTC, 1 for getting it (default).
    * getcrypto.getcur: Set the currency to display the price in, usd is the default.
"""

import requests
import time
import bumblebee.util
import bumblebee.input
import bumblebee.output
import bumblebee.engine
from requests.exceptions import RequestException

class Module(bumblebee.engine.Module):
    def __init__(self, engine, config):
        super(Module, self).__init__(engine, config,
            bumblebee.output.Widget(full_text=self.make)
        )
        self._curprice = ""
        self._nextcheck = 0
        self._interval = int(self.parameter("interval", "30"))

        engine.input.register_callback(self, button=bumblebee.input.LEFT_MOUSE,
            cmd="xdg-open https://www.livecoinwatch.com/")

    def make(self, widget):
        return self.text.strip()

    def update(self, widgets):
        if self._nextcheck < int(time.time()):
            self._nextcheck = int(time.time()) + self._interval
            try:
              eth = requests.get('https://api.coinmarketcap.com/v1/ticker/ethereum/?convert=USD',timeout=5).json()[0]
              btc = requests.get('https://api.coinmarketcap.com/v1/ticker/bitcoin/?convert=USD',timeout=5).json()[0]
            except:
              self.text = "unable to update prices"
            else:
              self.text = "Ξ %.2f Ƀ %.2f 🐬 %.2f%%" % (float(eth['price_usd']),float(btc['price_usd']),100. * float(eth['market_cap_usd']) / float(btc['market_cap_usd']))
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
