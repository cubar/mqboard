ESPTOOL="esptool.py --port /dev/ttyUSB0"
BIN="$1"

erase()
{
  $ESPTOOL erase_flash
}

flash()
{
  $ESPTOOL --chip esp32 --baud 460800 write_flash -z 0x1000 $BIN
}

if [ -z "$2" ]
then
    echo "Als eerste arg wordt een micropython bin file verwacht"
    echo "Tweede arg kan zijn 'erase' of 'flash'"
    echo "Als het tweede arg 'erase's kan een derde arg 'flash' zijn" 
    echo "'erase' leegt het filesysteem"
    echo "'flash' upload het micropython systeem van het eerste arg"
else
    $2
fi

if [ -n $3 ]; then $3; fi
