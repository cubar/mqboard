RS='rshell --port /dev/ttyUSB0'
cd image
(for dir in */
do
    echo "echo '    mkdir $dir'"
    echo "mkdir /pyboard/$dir"
done

for py in $(find * -type f)
do
    echo "cp $py /pyboard/$py"
done | sort) | $RS
