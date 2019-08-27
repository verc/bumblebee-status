# pylint: disable=C0111,R0903
# -*- coding: utf-8 -*-

"""Hue light control and notification

Requires the following python packages:
    * requests

Parameters:
    * hue.interval: Polling interval (default: 30).
    * hue.signal: Name of Hue device to notify signal message.
    * hue.click: program to execute when icon is clicked (default: luminance)
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
        self._nextcheck = 0
        self._interval = int(self.parameter("interval", "30"))

        engine.input.register_callback(self, button=bumblebee.input.LEFT_MOUSE,
            cmd="luminance")

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
              ratio = 100. * float(eth['market_cap_usd']) / float(btc['market_cap_usd'])
              icon = ['🌑','🌒','🌓','🌔','🌕'][min(int(ratio)/25,4)]
              self.text = "Ξ %.2f Ƀ %.2f %s %.2f%%" % (float(eth['price_usd']),float(btc['price_usd']),icon,ratio)
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
