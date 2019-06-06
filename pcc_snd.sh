#!/bin/bash
cd pcc/sender
export LD_LIBRARY_PATH=~/pcc/sender/src
cd app

num_flows=1
inter_flow_time=1 # In seconds

sender_pids=()
for (( i=0; i < $num_flows; i++ )); do
	./sendfile 10.0.0.2 9000 pcc_transfer_file &
    echo $!

    sender_pids+=("$!")
    #sender_pids=("$i" "${sender_pids[0]}")
    #sender_pids=("$!" "${sender_pids[0]}")
	#echo $sender_pids
	#sleep $inter_flow_time
done

echo ${#sender_pids[@]}


for pid in $sender_pids; do
	echo $pid
	kill $pid
	#sleep $inter_flow_time
done