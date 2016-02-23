 module add hgi/samtools/1.3
. /nfs/users/nfs_i/ic4/Projects/python3/bam2cram-check/ENV/bin/activate
export PYTHONPATH=$PYTHONPATH:/nfs/users/nfs_i/ic4/Projects/python3/bam2cram-check

bam_dir=$1
cram_dir=$2
log_dir=$3
output_dir=$4
issues_dir=$5

for f in $bam_dir/*
do
	mkdir -p $log_dir
	mkdir -p $output_dir
	mkdir -p $issues_dir

	bam_name=$(basename "$f")
	ext="${bam_name##*.}"
	fname="${bam_name%.*}"
  	if [ "$ext" = "bam" ]
  	then
  		
  		bam_file=$bam_dir"/"$bam_name
  		if [ -f $cram_dir"/"$bam_name".cram" ]
  		then
  			cram_file=$cram_dir"/"$bam_name".cram"
  		elif [ -f $cram_dir"/"$fname".cram" ]
  		then
  			cram_file=$cram_dir"/"$fname".cram"
  		else
  			echo "Somethings wrong, the cram homologuos with the bam "$bam_file" doesnt exist!"
  		fi

  		err_file=$issues_dir"/"$fname".err"
  		if [ -f $cram_file ]
  		then
  			echo $cram_file
  			bsub -R"select[mem>4000] rusage[mem=4000]" -M4000 -G hgi -o $output_dir"/"$fname".out" "python main.py -vvv -b "$bam_file" -c "$cram_file" -e "$err_file" --log "$log_dir"/"$fname".log"
  		else
        echo "Cram file is not a file: "$cram_file
      fi
  		echo $cram_file
  		echo $bam_file

  	fi
done



