# COPA Reproduction
CS244 Spring 2019 project to reproduce the USENIX paper Copa: Practical Delay-Based Congestion Control. You can read the full report [here] (https://reproducingnetworkresearch.wordpress.com/2019/09/27/cs-244-19-reproducing-copa/).

# Pantheon Results

1. To set up dependencies run `pip install .` in the outermost directory of this repo.
2. `cd pantheon-reproduction`
3. Run `./run.sh` to download and start aggregating Pantheon data. This script takes the following arguments:
	* -i : the directory to put all downloaded files into and to read files from.
	* -f : a file with the experiments to aggregate. Sample files are provided in each of the cellular, wired, recent_cellular, and recent_wired directories.
	* -t : to only run throughput aggregation.
	* -d : to only run delay aggregation.
	* -p : if specified the script tries to download the pdf or json files for aggregating throughput, otherwise it assumes they are already downloaded.
	* -l : if specified the script tries to download the log files for aggregating delay, otherwise it assumes they are already downloaded.
	* -r : if a json file of the statistics of the experiments is available on Pantheon, this will download the json files as opposed to the pdf files since json files are smaller. (check on Pantheon if the json files exist for the experiments in the file given before using this option)

	A sample command could be `./run.sh -i wired -f after_feb_19.txt -l -p` to do the throughput and aggregate delay for all experiments listed in after_feb_19.txt which is found in the wired directory and attempt to download the log and pdf files needed. Another command could be `./run.sh -i current_cellular -f cellular_names.txt -d -r` to run the aggregation for only the delay on the experiments in the cellular_names.txt file in the current_cellular directory. This command does not attempt to downloaded the necessary json files and assumes they already exist in the recent_cellular directory.

4. To obtain plots run `python final_aggregate_delay.py` with the following arguments:
	* -d : the path to a file with the delay results.
	* -t : the path to a file with the throughput results.
	* -p : if present the plot will show the comparison between these reproduction results and the original results in the paper. If this option is set it must specify if wired or cellular. If the option is not set the plot will just be of the reproduction results.

	The delay and throughput results should be available in the file specified for -i in the command in part 1.

# Jain Fairness Results

1. run `./jain_full_experiment.py.` The script takes the following arguments:
	* -bw: the bandwidth of the emulated link in Mb/s.
	* -d: the delay of the link in ms.
	* -q: the queue size of the link in packets.
	* -ift: the inter-flow time (i.e., the time between consecutive flow start and ends) in seconds.
	* -delta: how long to extent the throughput plots after the end of the experiment in seconds (e.g, with delta=1, a 20s experiment will be plotted with an x-axis from 0 to 21).
	* -num_flows: the number of flows to run.
	* -algs: a list of the congestion control protocols to compare.

By default, the parameters are set to match the settings used in the original paper, with the addition of the Reno and Vegas congestion control protocols. 

Note that occasionally the trace processing code will fail because the tcpdump program was cut off in the middle of logging a packet. If this happens, just rerun the script for the algorithm that experienced the issue.
	

