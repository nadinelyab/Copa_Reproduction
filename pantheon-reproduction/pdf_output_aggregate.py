import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("-d", type=str, help="directory with output files")
args = parser.parse_args()

cc_names = ["bbr",
			  "cubic",
			  "ledbat",
			  "pcc",
			  "quic",
			  "scream",
			  "webrtc",
			  "sprout",
			  "taova",
			  "vegas",
			   "verus",
			    "copa",
			    "fillp",
			    "indigo_1_32",
			     "vivace_latency",
			      "vivace_loss",
			       "vivace_lte"]

d = {"bbr": 0,
			  "cubic": 0,
			  "ledbat": 0,
			  "pcc": 0,
			  "quic": 0,
			  "scream": 0,
			  "webrtc": 0,
			  "sprout": 0,
			  "taova": 0,
			  "vegas": 0,
			   "verus": 0,
			    "copa": 0,
			    "fillp": 0,
			    "indigo_1_32": 0,
			     "vivace_latency":0,
			      "vivace_loss": 0,
			       "vivace_lte": 0}
num_files = 0
redo = {}
count_flows = {"bbr": 0, "cubic": 0,"ledbat": 0,"pcc": 0,"quic": 0,"scream": 0,"webrtc": 0,"sprout": 0,"taova": 0,"vegas": 0,"verus": 0,"copa": 0,"fillp": 0,"indigo_1_32": 0,"vivace_latency":0,"vivace_loss": 0,"vivace_lte": 0}
for filename in os.listdir(args.d):
	max_tput = 0
	if filename.endswith(".output"):
		num_files += 1
		temp = {"bbr": 0,
			  "cubic": 0,
			  "ledbat": 0,
			  "pcc": 0,
			  "quic": 0,
			  "scream": 0,
			  "webrtc": 0,
			  "sprout": 0,
			  "taova": 0,
			  "vegas": 0,
			   "verus": 0,
			    "copa": 0,
			    "fillp": 0,
			    "indigo_1_32": 0,
			     "vivace_latency":0,
			      "vivace_loss": 0,
			       "vivace_lte": 0}
		with open(filename) as file:
			line = file.readline()
			flow = 0
			while (line):
				flow += 1
				for cc in cc_names:
					t = file.readline()
					if(t == "N/A\n"):
						continue
					tput = float(t)
					if tput >= 120:
						if filename not in redo:
							redo[filename] = {cc: [flow]}
						elif cc not in redo[filename]:
							redo[filename][cc] = [flow]
						elif flow not in redo[filename][cc]:
							redo[filename][cc].append(flow)
						continue
					if tput > max_tput:
						max_tput = tput
					temp[cc] += tput
					count_flows[cc] += 1
				line = file.readline()
				if(line): 
					line = file.readline()
			for cc in temp:
				if count_flows[cc] > 0:
					d[cc] += temp[cc]/(max_tput)
for cc in d:
	d[cc] /= count_flows[cc]
print(d)
#print redo
