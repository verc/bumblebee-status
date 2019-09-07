# pylint: disable=C0111,R0903
# -*- coding: utf-8 -*-

"""Hue light control and notification

Requires the following python packages:
    * phue

Parameters:
    * hue.bridge: IP of Hue bridge.
    * hue.group: Name of group to control.
    * hue.action: action to execute when icon is right-clicked (default: luminance).

    * hue.interval: Polling interval in seconds (default: 5).
    * hue.sensor: Name of Sensor to read.
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
        while True:
          try:
            self.bridge = Bridge(self.parameter("bridge", ""))
            self.bridge.connect()
            for id, group in self.bridge.get_group().items():
              if group['name'] == self.parameter("group", ""):
                break
            break
          except:
            self.text = "error: could not connect to bridge at: " + self.parameter("bridge", "")
            time.sleep(1)

        if group['name'] != self.parameter("group", ""):
          self.text = "error: unknown group: " + self.parameter("group", "")
          return

        self.group = Group(self.bridge, int(id))
        self.brightness = self.group.brightness - self.group.brightness % 5
        self.original_brightness = self.group.brightness
        self.modify_brightness = False

        self._nextcheck = 0
        self._tempcheck = 0
        self._statecheck = 0
        self.on = self.group.on
        self._interval = int(self.parameter("interval", "1"))

        engine.input.register_callback(self, button=bumblebee.input.LEFT_MOUSE,
            cmd=self.click)
        engine.input.register_callback(self, button=bumblebee.input.RIGHT_MOUSE,
                                       cmd=self.parameter("action", "luminance"))
        engine.input.register_callback(self, button=bumblebee.input.WHEEL_UP,
                                       cmd=self.increase_brightness)
        engine.input.register_callback(self, button=bumblebee.input.WHEEL_DOWN,
                                       cmd=self.decrease_brightness)

        self.text = "%d%%" % self.brightness
        self.update(None)

    def click(self, e=None):
      self.group.on = self.on = not self.group.on
      self._statecheck = int(time.time()) + 1

    def increase_brightness(self, e=None):
      self.brightness += 5
      self.text = "%d%%" % self.brightness
      self.modify_brightness = True
      self._nextcheck = int(time.time()) + self._interval

    def decrease_brightness(self, e=None):
      self.brightness -= 5
      self.text = "%d%%" % self.brightness
      self.modify_brightness = True
      self._nextcheck = int(time.time()) + self._interval

    def make(self, widget):
      return self.text.strip()

    def state(self, widget):
      if self._statecheck < int(time.time()):
        self._statecheck = int(time.time()) + 1
        self.on = self.group.on
      if not self.on:
        return ["warning"]
      return ["default"]

    def update(self, widgets):
      if self._nextcheck < int(time.time()) and self.modify_brightness:
        self._nextcheck = int(time.time()) + self._interval
        group_brightness = self.group.brightness
        if self.brightness != group_brightness:
          if self.original_brightness == group_brightness:
            self.group.brightness = self.brightness
            self.original_brightness = self.brightness
          else:
            self.brightness = group_brightness
            self.original_brightness = group_brightness
        self.modify_brightness = False
      if self._tempcheck < int(time.time()):
        self._tempcheck = int(time.time()) + 10
        if self.parameter("sensor", ""):
          api = self.bridge.get_api()['sensors']
          sensors = {}
          for s in api:
            if api[s].get('productname', '') == 'Hue motion sensor' and api[s]['name'] == self.parameter("sensor", ""):
              sensors = {
                'motion': api[str(int(s) + 0)]['state'],
                'light': api[str(int(s) + 1)]['state'],
                'temperature': api[str(int(s) + 2)]['state']
              }
              break
          self.text = "%.2f°" % (float(sensors['temperature']['temperature'])/100,)
