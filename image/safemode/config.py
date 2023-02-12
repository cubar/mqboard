# config contains the configuration of the board, including which modules to load&run
# as well as settings for those modules.
# Copyright © 2020 by Thorsten von Eicken.

import secrets
from machine import unique_id
from binascii import hexlify

# kind tells us which type of board this is running.
# It is used in board to define LED pins.
# See board.py for supported kinds of boards.
kind = "esp22"

# directories to add to the system search path (after ["", "/lib"])
# this is not applied in safe mode
syspath = ["/src"]

# experimental settings to control MicroPython heap size, may move elsewhere...
# max_mp_heap = 300*1024  # max MP heap in bytes to limit GC with SPIRAM, or leave free space
# min_idf_heap = 120*1024  # min bytes left for esp-idf for wifi/tls/ble/... buffers

# use the unique_id of the esp module as first part of the topic
uniqueId = hexlify(unique_id()).decode()[-6:]

#
# Configuration of loaded modules
#
# The dicts below get passed to the start() function of the modules loaded by main.py.
# The name of each dict must match the name of the module.

mqtt = {  # refer to mqtt_async for the list of config options
    "server"    : secrets.mqtt_addr,
    "client_id" : uniqueId,
    # settings to make TLS work
    "port"      : secrets.mqtt_port,
    "ssl_params": { "server_hostname": secrets.mqtt_host },
    # user/pass for MQTT-level authentication
    "user"      : secrets.mqtt_user,
    "password"  : secrets.mqtt_pass,
    # ssid/pass for Wifi auth
    "ssid"      : secrets.wifi_ssid,
    "wifi_pw"   : secrets.wifi_pass,
}

# Python modules (aca: apps) to load and call start on.
# If module foo (in file foo.py) defines foo:
# then:
#     foo.start(mqtt, foo) is called
# else:
#     foo.start(mqtt, {})
# If there is no foo.start() then that's OK too,
# the module will just be imported for it's side effect.
modules = [ "mqtt", "logging", "mqrepl", "watchdog", "sysinfo", ]

# At last we configure each app using it's module name
mqrepl = {
    "prefix" : uniqueId + "/mqb/",  # prefix is before cmd/... or reply/...
}

watchdog = {
    "prefix"  : mqrepl["prefix"],  # must be mqrepl["prefix"]
    "timeout" : 60,   # watchdog timeout in seconds, default is 300
    "allok"   : 60,   # wait time in secs after connection before giving all-OK (no safe mode)
    "revert"  : True, # whether to revert from safe mode to normal mode after all-OK time
}

logging = {
    "topic"      : uniqueId + "/log",
    "boot_sz"    : 10*1024,  # large buffer at boot, got plenty of memory then
    "boot_level" :   10,     # 10=debug, 20=info, 30=warning (avoiding import logging)
    "loop_sz"    : 1024,     # more moderate buffer once connected
    "loop_level" :   10,     # 10=debug, 20=info, 30=warning (avoiding import logging)
}

# sysinfo task sends system info periodically; from github.com/tve/mpy-lib/sysinfo
sysinfo = {
    "topic"      : uniqueId + "/sysinfo",
    "interval"   : 60,  # interval in seconds, default is 60
}
