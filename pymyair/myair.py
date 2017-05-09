import requests
from util import etree_to_dict
import xml.etree.ElementTree as ElementTree
import pprint

# getSystemData
# {'iZS10.3': {'authenticated': '1',
#              'mac': 'xxxx',
#              'request': 'getSystemData',
#              'system': {'AppStore': 'MyAir5',
#                         'CBrev': '6.2',
#                         'MyAppRev': '11.110',
#                         'hasLights': '0',
#                         'name': 'AIRCON',
#                         'rID': None,
#                         'type': '17',
#                         'unitcontrol': {'activationCodeStatus': '0',
#                                         'airConErrorCode': None,
#                                         'airconOnOff': '1',
#                                         'availableSchedules': '5',
#                                         'centralActualTemp': '25.5',
#                                         'centralDesiredTemp': '26.0',
#                                         'fanSpeed': '4',
#                                         'filterCleanWarning': '0',
#                                         'maxUserTemp': '32.0',
#                                         'minUserTemp': '16.0',
#                                         'mode': '1',
#                                         'numberOfZones': '7',
#                                         'unitControlTempsSetting': '5'},
#                         'zoneStationHasUnitControl': '18',
#                         'zs103TechSettings': {'ACinfo': '1',
#                                               'FAstatus': '0',
#                                               'chucklesStatus': '0',
#                                               'dealerPhoneNumber': 'xxxx',
#                                               'logoPIN': 'xxxx',
#                                               'my3Gstatus': '0',
#                                               'numberofConstantZones': '1',
#                                               'returnAirOffset': '0.0',
#                                               'systemID': '1',
#                                               'tempSensorNotConfigured': '0',
#                                               'wifiStatus': '0',
#                                               'zsConstantZone1': '6',
#                                               'zsConstantZone2': '0',
#                                               'zsConstantZone3': '0'}}}}
# getZoneData
# {'iZS10.3': {'authenticated': '1',
#              'mac': 'xxxx',
#              'request': 'getZoneData',
#              'zone1': {'RFstrength': '59',
#                        'actualTemp': '26.0',
#                        'desiredTemp': '26.0',
#                        'hasClimateControl': '1',
#                        'hasLowBatt': '0',
#                        'maxDamper': '100',
#                        'minDamper': '0',
#                        'motionCurrentState': '0',
#                        'name': 'MAIN BED',
#                        'setting': '1',
#                        'tempSensorClash': '0',
#                        'userPercentAvail': '1',
#                        'userPercentSetting': '5'}}}

FAN_MAP = {'low' : 1, 'medium': 2, 'high': 3, 'auto': 4}
MODE_MAP = {'cool': 1, 'heat': 2, 'fan_only': 3, 'dry': 5}


class MyAir:
    def __init__(self, host, port=2025, key=None):
        self.host = host
        self.port = port
        self.key = key
        if (key):
            self.realkey = MyAir._manglekey(key)
        self.configured_zones = ()

    @staticmethod
    def _manglekey(key):
        key = MyAir._swap(key, 3, 27)
        key = MyAir._swap(key, 9, 17)
        return key

    @staticmethod
    def _swap(s, i, j):
        return ''.join((s[:i], s[j], s[i+1:j], s[i], s[j+1:]))

    def _request(self, request):

        # With introduction of MyPlace, all AES encryption appears to have been dropped (!) for LAN access.
        # If anyone has not upgraded their tablet, I may re-introduce this as required.
        # It's easier not to maintain this code if possible...
        #cipher = AESCipher(self.realkey)
        #enc_request = cipher.encrypt(request)

        url = "http://%s:%s/%s" % (self.host, self.port, request)

        r = requests.get(url)
        r.raise_for_status()

        data = r.content.decode('utf-8')
        
        try:
            tree = ElementTree.fromstring(data)
            entry = etree_to_dict(tree)
            
            return entry

        except ElementTree.ParseError:
            raise Exception("Found malformed XML at %s: %s", url, data)


    def getZone(self, id):
        #actualTemp
        #desiredTemp
        #name
        if id not in range(1,10):
            raise Exception("Invalid id: %s" % id)

        req = self._request("getZoneData?zone=%s" % id)
        zonedata = req.get('iZS10.3').get("zone%s" % id)

        return zonedata


    def getZones(self):
        zones = {}
        zonecount = self.getZoneCount()
        for id in range(1,zonecount+1):
            zones[id] =self.getZone(id)
        return zones

    def getZoneCount(self, systemdata=self.getSystem()):
        zonecount = int(systemdata.get('unitcontrol').get('numberOfZones'))
        return zonecount

    def setZone(self, id, state=None, target=None):
        #TODO check if state param defined or actually false
        # check target is int in defined range (minusertemp and maxusertemp)
        # limit to int, to maintain compatibility with myplace apps
        if (state == 'on'):
            self._request("setZoneData?zone=%s&zoneSetting=1" % id)
        elif (state == 'off'):
            self._request("setZoneData?zone=%s&zoneSetting=0" % id)

        if target:
            self._request("setZoneData?zone=%s&desiredTemp=%s.0" % target)

        # TODO check centralDesiredTemp in relation to constant zone..
        # TODO check what happens when temp sensors are not working
        #setZoneData?zone=1&zoneSetting=1
        #setZoneData?zone=1&desiredTemp=26.0
        #setSystemData?centralDesiredTemp=" + String.valueOf(f));

    def setSystem(self, state):
        # setSystemData?FAstatus=1,2   # Not sure what this is yet
        # setSystemData?fanSpeed=1,2,3,4  # 4 is likely to be auto

        if (state == 'off'):
            req = self._request("setSystemData?airconOnOff=0")
        else:
            if state in MODE_MAP:
                req = self._request("setSystemData?mode=%s" % MODE_MAP.get(state))
            else:
                raise Exception('invalid state: %s' % state)
            req = self._request("setSystemData?airconOnOff=1")
    

        
    def setFanSpeed(self, fanSpeed):
        if fanSpeed in FAN_MAP:
            self._request("setSystemData?fanSpeed=%s" % FAN_MAP.get(fanSpeed))   
        else:
            raise Exception('invalid fanSpeed: %s' % fanSpeed)


    def getSystem(self):
        req = self._request("getSystemData")
        return req.get('iZS10.3').get('system')

    def getFanSpeed(self, systemdata=self.getSystem()):
        fanspeed = systemdata.get('unitcontrol').get('fanSpeed')
        try:
            fanspeed_name = list(FAN_MAP.keys())[list(FAN_MAP.values()).index(fanspeed)]
            return fanspeed_name
        except DictError:
            return 'unknown'
        

    def getMode(self, systemdata=self.getSystem()):
        mode = systemdata.get('unitcontrol').get('mode')
        onoff = systemdata.get('unitcontrol').get('airconOnOff')
        if onoff == '0':
            return 'off'
        elif onoff == '1':
            try:
                mode_name = list(MODE_MAP.keys())[list(MODE_MAP.values()).index(mode)]
                return mode_name
            # TODO: find exception name
            except DictError:
                return 'unknown'


if __name__== "__main__":
    ma = MyAir("192.168.3.151")

    zonedata = ma.getZone(1)
    data = ma.getSystem()


    pp = pprint.PrettyPrinter()
    pp.pprint(zonedata)
    pp.pprint(data)

    pp.pprint(ma.getZones())
    