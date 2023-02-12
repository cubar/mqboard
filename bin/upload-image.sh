RS='rshell --port /dev/ttyUSB0'
cd image
for dir in */
do
    echo "    mkdir $dir"
    $RS mkdir /pyboard/$dir
done

for py in $(find * -type f)
do
    echo "    copying $py"
    $RS cp $py /pyboard/$py
done
