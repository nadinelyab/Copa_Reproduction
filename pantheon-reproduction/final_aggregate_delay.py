import ast
import pandas as pd
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-d", type=str, help="delay results")
parser.add_argument("-t", type=str, help="throughput results")
parser.add_argument("-p", type=str, help="type of link")
args = parser.parse_args()

avg_delay_final = {}
with open(args.d) as file:
	place = file.readline()
	count = 0
	while(place):
		count += 1
		curr_dict = ast.literal_eval(file.readline())

		for cc in curr_dict:
			if not cc in avg_delay_final:
				avg_delay_final[cc] = 0
			avg_delay_final[cc] += curr_dict[cc]

		place = file.readline()

	for cc in avg_delay_final:
			avg_delay_final[cc] /= count

with open(args.t) as file:
	tput_dict = ast.literal_eval(file.readline())

tput_df = pd.DataFrame(tput_dict.items())
delay_df = pd.DataFrame(avg_delay_final.items())
df = pd.merge(tput_df, delay_df, how='inner', on=0)
df = df.rename({0: "cc", "1_x": "tput", "1_y": "delay"}, axis='columns')
print df
max_delay = 0
min_delay = 10000000

if(args.p):
	if(args.p == 'wired'):
		original_data_file = 'paper_wired.txt'
	else:
		original_data_file = 'paper_cellular.txt'
	original_df = pd.read_csv(original_data_file, sep='\t')
	original_df.set_index('cc', inplace=True)

	colors = ['r', 'b', 'g', 'c', 'm', 'y', 'k']
	fig = plt.figure()
	ax = fig.add_subplot(111)
	for i, txt in enumerate(df.cc):
		try:
			other_row = original_df.loc[txt,:]
		except:
			continue
		if(df.delay[i] > max_delay):
			max_delay = df.delay[i]
		elif other_row.delay > max_delay:
			max_delay = other_row.delay
		elif min_delay > df.delay[i]:
			min_delay = df.delay[i]
		elif min_delay > other_row.delay:
			min_delay = other_row.delay
		plt.plot([df.delay[i], other_row.delay], [df.tput[i], other_row.tput], 
					colors[i%7]+'.--', linewidth=1)
		ax.annotate(txt, (other_row.delay,other_row.tput))
else:
	ax = df.plot.scatter(x='delay', y='tput')
	for i, txt in enumerate(df.cc):
	        if(max_delay < df.delay[i]):
	               max_delay = df.delay[i]
	        elif(min_delay > df.delay[i] and df.delay[i] > 0):
	        	min_delay = df.delay[i]
	        if(txt == 'pcc' or txt=='taova'):
	        	ax.annotate(txt, xy=(df.delay[i],df.tput[i]), xytext=(df.delay[i],df.tput[i] -.02))
	        else:
	        	ax.annotate(txt, xy=(df.delay[i],df.tput[i]), xytext=(df.delay[i],df.tput[i]))

ax.set_xscale('log', basex=2)

plt.xlabel('Avg. Queueing Delay (ms)')
plt.ylabel('Avg. Normalized Throughput')
max_delay += int(max_delay)*0.1
plt.ylim(0, 1)
plt.xlim(max_delay,0)
plt.show()