import safemode.config as conf
from machine import UART

kind = conf.kind
syspath = conf.syspath
uniqueId = conf.uniqueId
mqtt = conf.mqtt
modules = conf.modules
mqrepl = conf.mqrepl
watchdog = conf.watchdog
logging = conf.logging
sysinfo = conf.sysinfo

# sysinfo task sends system info periodically; from github.com/tve/mpy-lib/sysinfo
sysinfo = {
    "topic"      : uniqueId + "/sysinfo",
    "interval"   : 60,  # interval in seconds, default is 60
}

modules += [ 'lights', 'blinky', ]

# network time sync; from github.com/tve/mpy-lib/sntp
sntp = {
    "host"   : "pool.ntp.org",
    "zone"   : "CEST",
}

blinky = {  # blinks the boards default led, if any
    "topic"  : f'{uniqueId}/period',
    "period" : 800,  # initial period in milliseconds
}

lights = {  # switch and dimmer for low voltage (12V, 24V,...) led light
    "topic"  : f'{uniqueId}/light',
}
