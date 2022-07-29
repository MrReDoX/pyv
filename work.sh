filename=$(basename -- "$1")

cp "$1" .
python $filename
rm $filename
