This repo is heavily based on the work of Thorsten von Eicken on
  https://github.com/tve/mqboard.
It is here for my own convenience but someone might find it useful.

The setup of Thorsten is very solid:
You can upload new capabilities to your esp module by:
- adding a new script into the lib folder
- updating the config.py file in the lib folder
- resetting the board with:
  - mqb reset

You can recover from any bug in any of the scripts in the lib folder, even an "infinite loop",
because the MQTT connection will persist. This allows you to correct any mistakes by uploading
a known good set of scripts on the board.

You can also see log messages (mqb view) and in your code you can decide which level of messages you want to see.

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

See requirements.txt to understand which libs we need for the python environment to
communicate with your esp module.
Use rshell to interact with your esp board via USB. An Alias is handy:
- alias rs='rshell --port /dev/ttyUSB0'../Readme.md
Inside rshell you have a few linux-like commands where you can use a special folder:
- /pyboard
that refers to the filesystem on your esp module.
From your rshell prompt you can type:
- sync image /pyboard # upload all contents of image to the esp module
- repl                # Enter into interactive micropython mode on your esp module.

Communication via MQTT (mqb) is much faster then via USB (rshell).
After uploading the contents of the image folder to the esp module and setting you environment in the mqb script,
You need to set two environment variables:
- export MQBOARD_SERVER='10.0.0.1'    # the ip address of your MQTT server
- export MQBOARD_PREFIX='<board-id>' # the first string of the topic
This prefix is unique for every esp board and you can find it using the repl and looking for a line of the form:
- I 16:50:20.298 watchdog: === topic=3101a4/mqb/cmd/eval/0F00D/

The prefix would be "3101a4" in this example.

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
