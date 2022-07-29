file_names='./'$1'/*.py'

for file in $file_names
do
  ./work.sh $file &
done
