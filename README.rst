MyAir/MyPlace (Advantage Air) Python API
========================================

A simple Python API that wraps the HTTP based API exposed by the MyPlace
service that runs on Advantage Air supplied Android tablets. 

This library can be used to control the MyAir AC zoning system allowing:

 * On/Off Control
 * Mode Switching: Cool, Heat, Dry, Fan Only
 * Per Zone: On/Off, setting desiredTemp
 * Per Zone: Reading actualTemp (Not shown in Myplace app)

This API was reverse engineered from communication from the MyPlace app
(formerly MyAir 5) and only supports MyAir functionality (no MyLights)

TODO
----

 * Add support for systems without temperature sensors
 * Fix setting temperature of constant/myzone
 * Add discovery protocol from netdisco into this library
 * Push to pypi

Examples
--------

    ma = MyAir("192.168.1.33")
    zonedata = ma.getZone(1)

    print("ZONE 1: %s" % zonedata.get('name'))
    print("Current Temp: %sC" % zonedata.get('actualTemp'))
    print("Target Temp: %sC" % zonedata.get('targetTemp'))

    # Set temp
    ma.setZone(state='on',target=27)
    ma.setSystem('cool')

    ma.setSystem('off')

----

IP Address of WebService
------------------------
The webservice used by this API is the only available on the same LAN as the 
android tablet. Support for the two versions of remote access used by MyAir 
(mycloud,firebase) are not supported. You can find the IP of the android 
tablet in Wifi Settings - Advanced. If you do not use auto-discovery it's 
recommended to set your MyAir android tablet to set a static dhcp entry on your
router/dhcp server.

getZone
-------

Returns a dict minimally parsed directly from the MyPlace webservice similar to:

{'RFstrength': '59',
'actualTemp': '26.0',
'desiredTemp': '26.0',
'hasClimateControl': '1',
'hasLowBatt': '0',
'maxDamper': '100',
'minDamper': '0',
'motionCurrentState': '0',
'name': 'MAIN BED',
'setting': '1',
'tempSensorClash': '0',
'userPercentAvail': '1',
'userPercentSetting': '5'}

Of interest is the actualTemp (not exposed in the Mobile App), desiredTemp and setting (ON/OFF)

getZones
--------

This is a helper method to retrieve a status update for all zones.

Returns a dict indexed by zoneid (1..10) of all configured zones with the getZone output for each zone.
Note the underlying API doesn't implement a query to retrieve all zone data so this call is expensive as
it calls getSystem then getZone for each zone.

getSystem
---------

Returns a dict minimally parsed from the MyPlace webservice, for example:

{'AppStore': 'MyAir5',
 'CBrev': '6.2',
 'MyAppRev': '11.110',
 'hasLights': '0',
 'name': 'AIRCON',
 'rID': None,
 'type': '17',
 'unitcontrol': {'activationCodeStatus': '0',
                 'airConErrorCode': None,
                 'airconOnOff': '1',
                 'availableSchedules': '5',
                 'centralActualTemp': '25.5',
                 'centralDesiredTemp': '26.0',
                 'fanSpeed': '4',
                 'filterCleanWarning': '0',
                 'maxUserTemp': '32.0',
                 'minUserTemp': '16.0',
                 'mode': '1',
                 'numberOfZones': '7',
                 'unitControlTempsSetting': '5'},
 'zoneStationHasUnitControl': '18',
 'zs103TechSettings': {'ACinfo': '1',
                       'FAstatus': '0',
                       'chucklesStatus': '0',
                       'dealerPhoneNumber': 'xxxx',
                       'logoPIN': 'xxxx',
                       'my3Gstatus': '0',
                       'numberofConstantZones': '1',
                       'returnAirOffset': '0.0',
                       'systemID': '1',
                       'tempSensorNotConfigured': '0',
                       'wifiStatus': '0',
                       'zsConstantZone1': '6',
                       'zsConstantZone2': '0',
                       'zsConstantZone3': '0'}}

setSystem(state)
--------------

Where state is:
 * 'cool'
 * 'heat'
 * 'fan_only'
 * 'dry'
 * 'off'

setZone(state,target)
---------------------

For Example

ma.setZone(state='on',target=27)


setFanSpeed(fanSpeed)
---------------------

Where fanSpeed is:
 * 'low'
 * 'medium'
 * 'high'
 * 'auto'

Auto-Discovery
--------------

Currently not implemented in this library, however there is an implementation 
of the Advantage Air discovery protocol (over the LAN) in the netdisco project.
https://github.com/smallsam/netdisco

AES Encryption
--------------

Previously the MyAir controller communication was AES encrypted but this
appears to have been removed from the latest MyPlace service, presumably 
to improve performance on lower end devices. To make this library simpler
to maintain and debug going forward this support has been removed so you 
may need to update your MyAir tablet with the Apps (now MyPlace) from Play Store.
