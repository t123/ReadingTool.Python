echo "Processing forms"
for i in *.ui
do
	base=$(basename $i .ui)
	py="${base}.py"

	if [ $i -nt $py ]; then
		echo "pyuic4 $i > ../ui/views/$py"
		pyuic4 $i > ../ui/views/$py
	fi
done
