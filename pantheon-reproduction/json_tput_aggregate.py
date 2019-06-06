import argparse
import json
import os

parser = argparse.ArgumentParser()
parser.add_argument("-d", type=str, help="directory of flow information")
args = parser.parse_args()

# cc_names = ["bbr",
# 			  "cubic",
# 			  "ledbat",
# 			  "pcc",
# 			  "quic",
# 			  "scream",
# 			  "webrtc",
# 			  "sprout",
# 			  "taova",
# 			  "vegas",
# 			   "verus",
# 			    "copa",
# 			    "fillp",
# 			    "indigo_1_32",
# 			     "vivace_latency",
# 			      "vivace_loss",
# 			       "vivace_lte"]

d = {}

flow_count = {"bbr": 0,
			  "cubic": 0,
			  "ledbat": 0,
			  "pcc": 0,
			  "sprout": 0,
			  "vegas": 0,
			   "verus": 0,
			    "copa": 0,
			     "vivace":0}

cc_names = ["bbr", "copa", "cubic", "ledbat", "pcc", "sprout", "vegas", "verus", "vivace"]

num_files = 0
redo = {}
for filename in os.listdir(args.d):
	if filename.endswith(".json"):
	    num_files += 1
	    #temp = {"bbr": 0, "cubic": 0, "ledbat": 0, "pcc": 0, "sprout": 0, "vegas": 0, "verus": 0, "copa": 0, "vivace":0}
	    temp = {}
	    with open(args.d + "/" + filename) as file:
			throughput_json = file.readline()
			throughput_json = json.loads(throughput_json)

			max_tput = 0
			for cc in throughput_json:
				if cc not in flow_count:
					continue
				if cc not in d:
					d[cc] = 0
				if cc not in temp:
					temp[cc] = 0
				count = 0
				runs = throughput_json[cc]
				for r in runs:
					flows = runs[r]
					for f in flows:
						if f == 'all':
							continue
						vals = flows[f]
						if(vals['tput'] >= 120 and cc in cc_names):
							if filename not in redo:
								redo[filename] = {cc: {f: [r]}}
							elif cc not in redo[filename]:
								redo[filename][cc] = {f: [r]}
							elif f not in redo[filename][cc]:
								redo[filename][cc][f] = [r]
							else:
								redo[filename][cc][f].append(r)
							continue
						count += 1
						if(vals['tput'] > max_tput):
							max_tput = vals['tput']
						temp[cc] += vals['tput']
						flow_count[cc] += 1
				# if(count):
				# 	temp[cc] /= count

			for cc in temp:
				d[cc] += temp[cc]/max_tput

for cc in d:
	d[cc] /= flow_count[cc]
print(args.d)
print(d)