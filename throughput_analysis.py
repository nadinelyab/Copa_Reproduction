import dpkt
import math
import numpy as np
import os
import sys
from tqdm import tqdm

bucket_size=0.1 # in seconds
for alg in ['pcc']:

	pcap = dpkt.pcap.Reader(open(alg+'-trace', 'rb'))
	bucket_start = -1
	buckets, bucket, jain = {}, {}, {}
	prev_bucket = []
	flows = {}
	for ts, buf in tqdm(pcap):
		if bucket_start + bucket_size <= ts or bucket_start == -1:
			for x in bucket:
				bucket[x] /= ts - bucket_start
			if bucket != []:
				buckets[ts] = bucket
			tpts = [bucket[x] for x in bucket]
			if len(prev_bucket) != len(bucket):
				# Ignore these border cases for jain index as they may be inaccurate
				pass
			else:
				if tpts != []:
					jain[ts] = sum(tpts) ** 2 / (len(tpts) * sum([x ** 2 for x in tpts]))
				else: jain[ts] = 0
			prev_bucket = bucket
			bucket_start = ts
			bucket = {}
		
		try:
			eth = dpkt.ethernet.Ethernet(buf)
		except:
			continue

		if type(eth.data) == str or	type(eth.data.data) == str:
			continue
		if type(eth.data.data) != dpkt.tcp.TCP and type(eth.data.data) != dpkt.udp.UDP:
			continue

		if eth.data.data.dport in [5001, 8888, 9000]:
			if eth.data.data.sport not in flows:
				flows[eth.data.data.sport] = 1
			if eth.data.data.sport not in bucket:
				bucket[eth.data.data.sport] = 0
			bucket[eth.data.data.sport] += len(buf)

	tptfilename = '' + alg + '-trace' + "-tpt.dat"
	tptpolyfilename = '' + alg + '-trace' + "-tptpoly.dat"
	jainfilename = '' + alg + '-trace' + "-jain.dat"
	tptfile = open(tptfilename, 'w')
	tptpolyfile = open(tptpolyfilename, 'w')
	jainfile = open(jainfilename, 'w')
	timestamps = [x for x in buckets]
	timestamps.sort()
	flows = [x for x in flows]
	flows.sort()
	print(len(flows))
	print(flows)
	start_time = timestamps[0]
	for ts in timestamps:
		out = str(ts - start_time) + " "
		for x in flows:
			if x in buckets[ts]:
				out += str(buckets[ts][x] * 8e-6) + " "
			else:
				out += "0 "
		tptfile.write(out + "\n")
		if ts in jain:
			jainfile.write(str(ts - start_time) + " " + str(jain[ts]) + "\n")
	print("here")
	for ts in timestamps:
		tpts = [buckets[ts][x] for x in buckets[ts]]
		pltpt = 8e-6 * (np.mean(tpts) + np.std(tpts))
		if math.isnan(pltpt): continue
		if pltpt < 0: pltpt = 0
		tptpolyfile.write("%f %f\n" % (ts - start_time, pltpt))
	for ts in timestamps[::-1]:
		tpts = [buckets[ts][x] for x in buckets[ts]]
		pltpt = 8e-6 * (np.mean(tpts) - np.std(tpts))
		if math.isnan(pltpt): continue
		if pltpt < 0: pltpt = 0
		tptpolyfile.write("%f %f\n" % (ts - start_time, pltpt))

	#exit()
	tptgnufilename = '' + alg + '-trace' + "-tpt.gnuplot"
	tptgnufile = open(tptgnufilename, 'w')
	tptgnufile.write("""
	set terminal svg;
	set output '%s';

	set title "Dynamic behavior";
	set ylabel 'Throughput (Mbit/s)';
	set xlabel 'Time (s)';
	set xrange [0:105];
	set yrange [1:100];

	set logscale y;
	set key off;
	""" % ('' + alg + '-trace' + "-tpt.svg"))
	tptgnucmd = "plot "
	for i in range(len(flows)):
		tptgnucmd += "'%s' using 1:%d with lines, " % (tptfilename, i+2)
	tptgnufile.write(tptgnucmd)
	tptgnufile.close

	jaingnufilename = '' + alg + '-trace' + "-jain.gnuplot"
	jaingnufile = open(jaingnufilename, 'w')
	jaingnufile.write("""
	set terminal svg;
	set output '%s';

	set title "Dynamic behavior";
	set ylabel 'Jain index';
	set xlabel 'Time (s)';
	set xrange [0:105];
	set yrange [0:1];
	set key off;

	plot '%s' using 1:2 with lines
	""" % ('' + alg + '-trace' + "-jain.svg", jainfilename))

	print("gnuplot -p %s" % tptgnufilename)
	print("inkscape -A %s %s" % ('' + alg + '-trace' + "-tpt.pdf", '' + alg + '-trace' + "-tpt.svg"))
	print("gnuplot -p %s" % jaingnufilename)
	print("inkscape -A %s %s" % ('' + alg + '-trace' + "-jain.pdf", '' + alg + '-trace' + "-jain.svg"))