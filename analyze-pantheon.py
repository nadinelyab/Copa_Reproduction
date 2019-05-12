directory = "2019-04-24T00-10-AWS-California-1-to-Stanford-5-runs-3-flows"
cc_names = ["bbr", "copa", "cubic", "ledbat", "pcc", "sprout", "vegas", "verus", "vivace"]
filename = "_datalink_run"

tot_avg_tput = [0,0,0]
tot_avg_delay = [0,0,0]

for cc in cc_names:
	for i in range(1,6):
		count = [0,0,0]
		tput = [0,0,0]
		delays = [[], [], []]
		with open(directory + "/" + cc + filename + str(i) + ".log") as file:
			timestamp = file.readline()
			line = file.readline()
			while line:
				vals = line.split()
				if(vals[1] == "-"):
					flow = int(vals[4]) -1
					d = float(vals[3])
					byts = int(vals[2])
					count[flow] += 1
					tput[flow] += byts/d
					delays[flow].append(d)
				line = file.readline()
			tput = [t/c for t,c in zip(tput, count)]
			delays = [[d - m for d in q] for (q,m) in [[q, min(q)] for q in delays]]
			delays = [sum(l) for l in delays]
			delays = [d/c for d,c in zip(delays, count)]

		tot_avg_tput = [tot + t for tot,t in zip(tot_avg_tput, tput)]
		tot_avg_delay = [tot + d for tot,d in zip(tot_avg_delay, delays)]

	tot_avg_delay = [t/5 for t in tot_avg_delay]
	tot_avg_tput = [t/5 for t in tot_avg_tput]

	print(cc)
	print("tput" + str(tot_avg_tput))
	print("delay" + str(tot_avg_delay))