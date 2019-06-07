#!/bin/bash
tput_only=false
delay_only=false
download_pdfs=false
download_logs=false
recent=false
dir="."
while [[ $# -gt 0 ]] ; do
	key="$1"
	case $key in
		-t)
		tput_only=true
		shift
		;;
		-d)
		delay_only=true
		shift
		;;
		-p)
		download_pdfs=true
		shift
		;;
		-l)
		download_logs=true
		shift
		;;
		-i)
		dir=$2
		shift
		shift
		;;
		-f)
		f=$2
		shift
		shift
		;;
		-r)
		recent=true
		shift
		;;
	esac
done

file_names=()
cd $dir

while read -r line
do
	file_names+=("$line")
done < $f


http="https://s3.amazonaws.com/stanford-pantheon/real-world"
pdf_prefix="-pantheon-report.pdf"
tar_prefix=".tar.gz"
json_prefix="-pantheon-perf.json"


pdf_filenames=()
log_filenames=()
json_filenames=()

for l in "${file_names[@]}"
do
     country="$(cut -d ' ' -f 1 <<< $l)"
     file="$(cut -d ' ' -f 2 <<< $l)"
     pdf_filenames+=("$http/$country/reports/$file$pdf_prefix")
     log_filenames+=("$http/$country/$file$tar_prefix")
     json_filenames+=("$http/$country/reports/$file$json_prefix")
done

if ! $delay_only
current_time=$(date "+%Y.%m.%d-%H")
then
	if $recent
	then
		for i in "${!json_filenames[@]}"
		do
			file=$(echo "${json_filenames[$i]}" | cut -d '/' -f 8)
			if $download_pdfs && [ ! -f $file ]; then
				wget "${json_filenames[$i]}"
			fi
		done
		current_time=$(date "+%Y.%m.%d-%H")
		python ../json_tput_aggregate.py -d "." > $current_time"_tput_results.txt"
	else
		for i in "${!pdf_filenames[@]}"
		do
			file=$(echo "${pdf_filenames[$i]}" | cut -d '/' -f 8)
			if $download_pdfs && [ ! -f $file ]; then
				wget "${pdf_filenames[$i]}"
			fi

			if echo $file | grep -q "flows"; then
				pdf2txt.py -p 3 $file | sed -n '53, 108 p' > "$file.output"
				#| sed -e "6,8d;10d;14,15d;25,27d;29d;33,34d;44,46d;48d;52,53d" > "$file.output"
			else
				pdf2txt.py -p 3 $file | sed -n '55, 72 p' > "$file.output"
				#| sed -e "6,8d;10d;14,15d" > "$file.output"
			fi
		done
		python ../pdf_output_aggregate.py -d "." > $current_time"_tput_results.txt"
	fi
fi

if ! $tput_only
then
	current_time=$(date "+%Y.%m.%d-%H")
	for i in "${!log_filenames[@]}"
	do
		file=$(echo "${log_filenames[$i]}" | cut -d '/' -f 7)
		if $download_logs && [ ! -f $file ]; then
			wget ${log_filenames[$i]}
		fi
		directory=$(echo $file | cut -d '.' -f 1)
		if [ ! -d $directory ]; then
			echo "Untarring ..."
		    tar -xf $file
		fi
		python ../avg_delay.py -d $directory >> $current_time"_delay_results.txt"
		rm -rf $directory
	done
fi
