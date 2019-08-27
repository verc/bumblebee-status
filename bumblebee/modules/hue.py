# pylint: disable=C0111,R0903
# -*- coding: utf-8 -*-

"""Hue light control and notification

Requires the following python packages:
    * requests

Parameters:
    * hue.bridge: IP of Hue bridge.
    * hue.group: Name of group to control.
    * hue.action: action to execute when icon is right-clicked (default: luminance).

    * hue.interval: Polling interval in seconds (default: 5).
    * hue.signal: Name of Hue device to notify signal message (default: None).
"""

import requests
import time
import bumblebee.util
import bumblebee.input
import bumblebee.output
import bumblebee.engine
from phue import Bridge, Group

class Module(bumblebee.engine.Module):
    def __init__(self, engine, config):
        super(Module, self).__init__(engine, config,
            bumblebee.output.Widget(full_text=self.make)
        )
        try:
          self.bridge = Bridge(self.parameter("bridge", ""))
          self.bridge.connect()
        except:
          self.text = "error: could not connect to bridge at: " + self.parameter("bridge", "")
          return

        for id,group in self.bridge.get_group().items():
          if group['name'] == self.parameter("group", ""):
            break
        if group['name'] != self.parameter("group", ""):
          self.text = "error: unknown group: " + self.parameter("group", "")
          return

        self.group = Group(self.bridge, int(id))
        self.brightness = self.group.brightness - self.group.brightness % 5
        self.text = '⚫'

        self._nextcheck = 0
        self._interval = int(self.parameter("interval", "2"))

        engine.input.register_callback(self, button=bumblebee.input.LEFT_MOUSE,
            cmd=self.click)
        engine.input.register_callback(self, button=bumblebee.input.RIGHT_MOUSE,
                                       cmd=self.parameter("action", "luminance"))
        engine.input.register_callback(self, button=bumblebee.input.WHEEL_UP,
                                       cmd=self.increase_brightness)
        engine.input.register_callback(self, button=bumblebee.input.WHEEL_DOWN,
                                       cmd=self.decrease_brightness)

    def click(self, e=None):
      self.group.on = not self.group.on

    def increase_brightness(self, e=None):
      self.brightness += 5
      self.brightness = min(self.brightness, 100)
      self.text = "%d%%" % self.brightness

    def decrease_brightness(self, e=None):
      self.brightness -= 5
      self.brightness = max(self.brightness, 0)
      self.text = "%d%%" % self.brightness

    def make(self, widget):
      return self.text.strip()

    def state(self, widget):
      if not self.group.on:
        return ["warning"]
      return ["default"]

    def update(self, widgets):
      if self._nextcheck < int(time.time()):
        self._nextcheck = int(time.time()) + self._interval
        self.group.brightness = self.brightness
        self.text = '⚫'