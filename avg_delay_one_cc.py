import argparse
import ast
import os
from tqdm import tqdm

toolbar_width = 40
parser = argparse.ArgumentParser()
parser.add_argument("-d", type=str, help="directory with output files")
args = parser.parse_args()

cc_names = ["bbr", "cubic", "ledbat", "pcc", "sprout", 
			"vegas", "verus", "copa", "vivace_latency", "vivace_loss", "vivace_lte"]

avg_delays = {}


run_count = {"bbr": 0, "cubic": 0, "ledbat": 0, "pcc": 0, "sprout": 0, 
"vegas": 0, "verus": 0, "copa": 0, "vivace_latency": 0, "vivace_loss": 0, "vivace_lte":0}
if "flows" in args.d:
	n = 3
else:
	n = 1

skipped = []
f = open('redo_json.txt')
skip_dict = ast.literal_eval(f.readline())
for filename in tqdm(os.listdir(args.d)):
	dl_index = filename.find("datalink")
        run = filename.find("run") + 3
	#if filename.startswith(tuple(cc_names)) and dl_index is not -1:
		#if(filename.startswith("pcc_experimental")):
			#continue
	cc = filename[:(dl_index-1)]
	if not cc in avg_delays:
	    avg_delays[cc] = 0
	if not cc in run_count:
	    run_count[cc] = 0
	with open(args.d + "/" + filename) as file:
		flow_min = []
		flow_tot = []
		flow_count = []
		for i in range(n):
			flow_min.append(1000)
			flow_tot.append(0)
			flow_count.append(0)
		for line in file:
			words = line.split()
			if("-" in words):
				flow_num = int(words[4]) - 1
				delay = float(words[3])
				if (args.d in skip_dict
				   and cc in skip_dict[args.d]
				   and str(flow_num+1) in skip_dict[args.d][cc]):
				   #and filename[run] in skip_dict[args.d][cc][str(flow_num+1)]):
					if (cc, flow_num+1, filename[run]) not in skipped:
						skipped.append((cc, flow_num+1, filename[run]))
					continue	
				if delay < flow_min[flow_num]:
					flow_min[flow_num] = delay
				flow_count[flow_num] += 1
				flow_tot[flow_num] += delay
		results = [(t-c*m)/c for (t, m, c) in zip(flow_tot, flow_min, flow_count) if c > 0]
		run_count[cc] += sum(x > 0 for x in flow_count)
		avg_delays[filename[:(dl_index -1)]] += sum(results)
for cc in avg_delays:
	if run_count[cc] > 0:
		avg_delays[cc] /= run_count[cc]
print(args.d)
print(avg_delays)
