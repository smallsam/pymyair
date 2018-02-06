===========================
API for Advantage Air MyAir
===========================


.. image:: https://img.shields.io/pypi/v/pymyair.svg
        :target: https://pypi.python.org/pypi/pymyair

.. image:: https://img.shields.io/travis/smallsam/pymyair.svg
        :target: https://travis-ci.org/smallsam/pymyair

.. image:: https://readthedocs.org/projects/pymyair/badge/?version=latest
        :target: https://pymyair.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/smallsam/pymyair/shield.svg
     :target: https://pyup.io/repos/github/smallsam/pymyair/
     :alt: Updates


A simple Python API that wraps the HTTP based API exposed by the MyPlace service that runs on Advantage Air supplied Android tablets.

It can be used to control the MyAir 5 AC zoning system from Advantage Air.

* Free software: MIT license

Features
--------

* Zone setting, on/off. Temperature set points or percentage
* Per AC, on/off, heat/dry/vent
* Fan speed adjustment
* MyZone setting
* Reading current temperature of each zone *Not available in supplied apps*
* Access to system and zone level info
* CLI interface

Quickstart
----------

CLI
::

    pip install pymyair
    myair --help
    myair 192.168.1.120 zones
    myair 192.168.1.120 on
    myair 192.168.1.120 set --zone 3 --temp 26 --state on

API
::

    from pymyair.pymyair import MyAir

    ma = MyAir(host="192.168.1.120")
    ma.update()
    ma.mode = 'on'
    ma.myzone = 6
    ma.setZone(id=3, state='on', set_temp=26)


IP Address of WebService
-------------------------
The webservice used by this API is the only available on the same LAN as the 
android tablet. There is no support for the remote access APIs used by MyAir.
You can find the IP of the android tablet in Wifi Settings - Advanced.
It's recommended to set your MyAir android tablet to set a static dhcp entry on your
router/dhcp server.


Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

