This repo is heavily based on the work of Thorsten von Eicken on
  https://github.com/tve/mqboard.
It is here for my own convenience but someone might find it useful.

The setup of Thorsten is very solid:
You can upload new capabilities to your esp module by:
- adding a new script into the lib folder
- updating the config.py file in the lib folder
- resetting the board with:
  - mqb reset

So if you'd like to give it a try you will need:
- a MQTT broker and its credentials.
- a micropython esp32 (or esp8066) firmware.
  I used <a
  href='http://micropython.org/resources/firmware/esp32-20220618-v1.19.1.bin'>esp32-20220618-v1.19.1.bin</a>.
  You can find the newest files on <a href='https://micropython.org/download/esp32/'>micropython
  firmware page</a>.
- a python virtual environment: pip install -r requirements.txt

For convenience you could add the bin folder to your PATH environment variable.

To upload micropython to your esp module go the the bin folder and:
- cd bin
- wget http://micropython.org/resources/firmware/esp32-20220618-v1.19.1.bin
- ./32flash.sh esp32-20220618-v1.19.1.bin erase flash

Set your credentials in image/safemode/secrets.py.
To put all python scripts in the image/ folder on you board you can use:
- bin/upload-image.sh

See requirements.txt to understand which libs we need for the python environment to
communicate with your esp module.
Use rshell to interact with your esp board via USB. An Alias is handy:
- alias rs='rshell --port /dev/ttyUSB0'../Readme.md
Inside rshell you have a few linux-like commands where you can use a special folder:
- /pyboard
that refers to the filesystem on your esp module.
From your rshell prompt you can type:
- repl
to enter repl mode where you can type micropython directly on your esp module.

Communication via MQTT (mqb) is much faster then via USB (rshell).
Set you environment in the mqb script.
You can do:
- mqb ls                               # see what files are in the filesystem of your esp module
- mqb sync sync-image                  # upload all files in the image folder to you esp module
- mqb put <local_file> <remote_file>   # upload a single file
- mqb get <remote_file> [<local_file>] # download a file from your esp module
- mqb reset                            # reboot your esp module
- mqb eval a=123                       # evaluate a python command on your esp module
- mqb eval a                           # evaluate and retrieve the result (python variable of
                                       # previous commands still exist on your esp module)
- mqb                                  # display help
- mqb sync <sync_file>                 # upload files that were changed
