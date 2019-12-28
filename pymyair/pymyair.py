# -*- coding: utf-8 -*-

"""Main module."""

# API based on Specification published at
# http://advantageair.proboards.com/thread/2/api-document
# Requires signup, this is intended so that you can be informed of changes
# to the spec
from __future__ import absolute_import

import requests
import json
import time

FAN_MAP = {'low': 1, 'medium': 2, 'high': 3, 'auto': 4}
MODE_MAP = {'cool': 1, 'heat': 2, 'fan': 3, 'dry': 5}

# TODO: check fan mode (docs say vent, is it the same?)


class MyAir(object):
    def __init__(self, host, port=2025, aircon="ac1"):
        '''Params are host, port(default=2025), aircon(default="ac1")'''
        self._host = host
        self._port = port
        self._aircon = aircon
        self._system = None
        self._zones = None

    def _request(self, request):

        url = "http://%s:%s/%s" % (self._host, self._port, request)

        r = requests.get(url)
        r.raise_for_status()

        data = r.content.decode('utf-8')

        try:
            entry = json.loads(data)

            return entry

        except json.AttributeError:
            raise Exception("Found malformed JSON at %s: %s", url, data)

    def update(self):
        '''Fetch current state from MyAir'''
        # getSystemData can be somewhat unreliable
        # so we retry a number of times before giving up
        req = self._request("getSystemData")
        retry = 0
        sleep = 0.01
        while len(req) == 0 and retry < 30:
            retry = retry + 1
            if sleep < 5:
                sleep = sleep * 2
            time.sleep(sleep)
            req = self._request("getSystemData")
        if len(req) == 0:
            raise Exception("getSystemData failed")

        self._system = req
        return self._system

    @property
    def aircons(self):
        '''Returns a list of aircon identifiers,
        useful if you have more than one AC unit
        attached to your MyAir system'''
        return json.dumps(self.system['aircons'].keys)

    @property
    def zones(self):
        if not self._system:
            raise Exception('Need to call update()')
        return self.system['aircons'][self._aircon]['zones']

    @zones.setter
    def zones(self, update):
        '''Set zone(s) state, setTemp/value (Temp vs Percentage) using structure
        {"z02":{"state":"open"}}
        {"z04":{"setTemp":25},"z06":{"setTemp":25}}
        '''
        setjson = {self._aircon: {"zones": update}}
        valid_json = json.loads(setjson)

        self._request("setAircon?json=%s" % json.dumps(valid_json))

    def setTemp(self, set_temp=None):
        '''Set global temperature'''

        if set_temp in range(16, 32):
            setjson = "{\"ac1\":{\"info\":{\"setTemp\":%d}}}" % set_temp
        else:
            raise Exception(
                "temp needs to be in range 16-32, temp: %s" % set_temp)

        self._request("setAircon?json=%s" % setjson)

    def setZone(self, id, state=None, set_temp=None, value=None):
        '''Set zone state[on|off], set_temp or value (temp sensor/percent)'''

        # TODO: update string concat to json object

        if state == 'open' or (
                state != 'close' and
                state != 'off' and
                state != '0' and
                state):
            state_value = 'open'
        else:
            state_value = 'close'

        zoneid = "z%02d" % id

        setjson = "{\"%s\":{\"zones\":{\"%s\":{" % (self._aircon, zoneid)

        if state is not None and state_value:
            setjson += "\"state\":\"%s\"" % state_value

        if self.system['aircons'][self._aircon]['zones'][zoneid]['type'] > 0:
            # temperature sensor available
            if value and set_temp is None:
                raise Exception(
                    "zone requires setting by set_temp as it has temp sensor")
            if set_temp in range(16, 32):
                if state:
                    setjson += ","
                setjson += "\"setTemp\":%d" % set_temp
            else:
                raise Exception(
                    "temp needs to be in range 16-32, temp: %s" %
                    set_temp)
        else:
            # percentage set value for zone
            if value:
                if state:
                    setjson += ","
                setjson += "\"value\":%d" % value

        setjson += "}}}}"
        self._request("setAircon?json=%s" % setjson)

    @property
    def system(self):
        '''Returns complete system information from MyPlace Service'''
        if not self._system:
            raise Exception('Need to call update()')
        return self._system

    # Accessors for global mode, fanspeed
    @property
    def mode(self):
        '''Current set mode, 'off', 'heat', 'cool', 'dry', 'vent'.'''
        mode = self.system['aircons'][self._aircon]['info']['mode']
        onoff = self.system['aircons'][self._aircon]['info']['state']
        if onoff == 'off':
            return 'off'
        elif onoff == 'on':
            return mode

    @mode.setter
    def mode(self, mode):
        '''Set mode of AC: 'off', 'heat', 'cool', 'dry', 'vent'.'''
        # Ensure we're online
        self.system

        if (mode in ('off', 'on')):
            setjson = {self._aircon: {"info": {"state": mode}}}
            self._system['aircons'][self._aircon]['info']['state'] = mode
        elif mode in MODE_MAP:
            setjson = {self._aircon: {"info": {"state": "on", "mode": mode}}}
            self._system['aircons'][self._aircon]['info']['mode'] = mode
            self._system['aircons'][self._aircon]['info']['state'] = 'on'
        else:
            raise Exception('invalid state: %s' % mode)

        return self._request("setAircon?json=%s" % json.dumps(setjson))

    @property
    def myzone(self):
        '''Current MyZone'''
        return self.system['aircons'][self._aircon]['info']['myZone']

    @myzone.setter
    def myzone(self, val):
        '''Set MyZone [1-10]'''
        self.system

        if val in range(1, 10):
            setjson = {self._aircon: {"info": {"myZone": val}}}
            self._system['aircons'][self._aircon]['info']['myZone'] = val
            return self._request("setAircon?json=%s" % json.dumps(setjson))
        else:
            raise Exception('invalid myZone')

    @property
    def fanspeed(self):
        '''Current fanspeed, 'low', 'medium', 'high', 'auto'.'''
        return self.system['aircons'][self._aircon]['info']['fan']

    @fanspeed.setter
    def fanspeed(self, val):
        '''Set fanspeed:  'low', 'medium', 'high', 'auto'.'''
        # Ensure we're online
        self.system

        if val in FAN_MAP:
            setjson = {self._aircon: {"info": {"fan": val}}}
            self._system['aircons'][self._aircon]['info']['fan'] = val
            return self._request("setAircon?json=%s" % json.dumps(setjson))
        else:
            raise Exception('invalid fanSpeed, valid speeds:' + str(FAN_MAP))
