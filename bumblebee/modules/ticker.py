# pylint: disable=C0111,R0903

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
        self._interval = int(self.parameter("interval", "120"))
        self.tokens = ','.join([ tok.upper() for tok in self.parameter("tokens", "eth,btc").split(',') ])
        self.currency = self.parameter("currency", "usd").upper()

        engine.input.register_callback(self, button=bumblebee.input.LEFT_MOUSE,
            cmd="xdg-open https://www.livecoinwatch.com/")

    def make(self, widget):
        return self.text.strip()

    def update(self, widgets):
        if self._nextcheck < int(time.time()):
            self._nextcheck = int(time.time()) + self._interval
            try:
             r = requests.get('https://min-api.cryptocompare.com/data/pricemultifull?fsyms=%s&tsyms=%s' % (self.tokens,self.currency),timeout=5).json()
            except:
              self.text = "unable to update prices"
            else:
              self.text = ""
              for tok in self.tokens.split(','):
                self.text += tok + ' ' + str(r['RAW'][tok][self.currency]['PRICE']) + '  '
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
