from mininet.topo import Topo 
from mininet.node import CPULimitedHost 
from mininet.clean import cleanup 
from mininet.net import Mininet 
from mininet.link import TCLink 
from mininet.node import OVSController 
from mininet.util import dumpNodeConnections 
from mininet.cli import CLI 
from time import sleep, time 
import os 
import dpkt 
import math 
import numpy as np 
import sys 
from tqdm import tqdm 
import subprocess 
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-bw", type=int, default=46, help="link bandwidth in Mbits/s")
parser.add_argument("-d", type=int, default=10, help="link delay in ms (1/2 RTT)")
parser.add_argument("-q", type=int, default=77, help="queue size (in packets)")
parser.add_argument("-ift", type=int, default=1, help="inter-flow time")
parser.add_argument("-delta", type=int, default=0, help="extend graphs past end of experiment")
parser.add_argument("-num_flows", type=int, default=10)
parser.add_argument("-algs", nargs='*', default=['markovian', 'cubic', 'bbr', 'pcc', 'reno', 'vegas'],
                    help="list of algorithms to test")

args = parser.parse_args()

def run(node, cmd): 
    x = node.popen(cmd, shell=True) 
    print(x.communicate()) 
  
class CTopo(Topo): 
     
    def build(self): 
        hosts = [] 
        for i in range(2): 
            hosts.append(self.addHost('h' +str(i+1))) 
        self.addLink(hosts[0], hosts[1], bw=args.bw,  
                     max_queue_size=args.q, delay=str(args.d)+'ms') 
  
  
idntifier = str(args.bw)+"_"+str(args.d)+"_"+str(args.q)+"_"+str(args.ift)+"_"+str(args.num_flows)+"_" 
algs = args.algs
delta = args.delta
num_flows = args.num_flows
inter_flow_time = args.ift
  
for alg in algs: 
    print(alg)
    cleanup() 
 
    topo = CTopo() 
    net = Mininet(topo = topo, host=CPULimitedHost, link=TCLink, controller = OVSController) 
    net.start() 
  
    dumpNodeConnections(net.hosts) 
  
    net.pingAll() 
  
    h2 = net.get('h2') 
    h1 = net.get('h1') 

    if alg == 'markovian': 
        h2.popen('./pantheon/third_party/genericCC/receiver') 
    elif alg in ['cubic', 'bbr', 'reno', 'vegas']: 
       h2.popen('iperf -s -w 16m') 
    elif alg == 'pcc': 
        h2.popen('./pcc_rcv.sh') 
  
    p = h1.popen('tcpdump -w ' + idntifier + alg + '-trace -i h1-eth0 -n') 
    start = time() 
    ps = [] 
    for i in range(num_flows): 
        onduration = 2*(inter_flow_time*(num_flows-i)) 
        print(onduration)
        if alg == 'markovian': 
            p = h1.popen('timeout ' + str(onduration) + ' ' + 
                         './pantheon/third_party/genericCC/sender serverip='+h2.IP() +  
                         ' offduration=0 cctype='+ alg + ' \
                          delta_conf=do_ss:auto:0.5 traffic_params=deterministic,num_cycles=1 onduration=' + str(onduration*1000)) 
        elif alg == 'cubic': 
            p = h1.popen('iperf -c ' + h2.IP() + ' -Z cubic -t ' + str(onduration) + ' -p 5001') 
        elif alg == 'bbr': 
            p = h1.popen('iperf -c ' + h2.IP() + ' -Z bbr -t ' + str(onduration) + ' -p 5001') 
        elif alg == 'reno': 
            p = h1.popen('iperf -c ' + h2.IP() + ' -Z reno -t ' + str(onduration) + ' -p 5001') 
        elif alg == 'vegas': 
            p = h1.popen('iperf -c ' + h2.IP() + ' -Z vegas -t ' + str(onduration) + ' -p 5001') 
        elif alg == 'pcc': 
            p = h1.popen('bash -c "LD_LIBRARY_PATH=/home/sawyerb/pcc/sender/src ' + 
                ' timeout ' + str(onduration) + ' ./pcc/sender/app/sendfile '  
                + h2.IP() + ' 9000 pcc/sender/app/pcc_transfer_file"', shell=True) 
        ps.append(p) 
        sleep(inter_flow_time) 

    for i in range(num_flows): 
        print(ps[-1-i].communicate()) 
    print(time()-start) 
    cleanup() 
    sleep(4) 


bucket_size=0.1 # in seconds 

for alg in algs: 
    pcap = dpkt.pcap.Reader(open(idntifier + alg+'-trace', 'rb')) 
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
 
        if type(eth.data) == str or type(eth.data.data) == str: 
            continue 
        if type(eth.data.data) != dpkt.tcp.TCP and type(eth.data.data) != dpkt.udp.UDP: 
            continue 

        if eth.data.data.dport in [5001, 8888, 9000]: 
            if eth.data.data.sport not in flows: 
                flows[eth.data.data.sport] = 1 
            if eth.data.data.sport not in bucket: 
                bucket[eth.data.data.sport] = 0 
            bucket[eth.data.data.sport] += len(buf) 

    tptfilename = '' + idntifier + alg + '-trace' + "-tpt.dat" 
    tptpolyfilename = '' + idntifier + alg + '-trace' + "-tptpoly.dat" 
    jainfilename = '' + idntifier + alg + '-trace' + "-jain.dat" 
    tptfile = open(tptfilename, 'w') 
    tptpolyfile = open(tptpolyfilename, 'w') 
    jainfile = open(jainfilename, 'w') 
    timestamps = [x for x in buckets] 
    timestamps.sort() 
    flows = [x for x in flows] 
    flows.sort() 
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
    tptgnufilename = '' + idntifier + alg + '-trace' + "-tpt.gnuplot" 
    tptgnufile = open(tptgnufilename, 'w') 
    tptgnufile.write(""" 
    set terminal svg; 
    set output '%s'; 
  
    set title "Dynamic behavior"; 
    set ylabel 'Throughput (Mbit/s)'; 
    set xlabel 'Time (s)'; 
    set xrange [0:%d]; 
    set yrange [1:100]; 
  
    set logscale y; 
    set key off; 
    """ % ('' + alg + '-trace' + "-tpt.svg", (num_flows*inter_flow_time*2)+delta)) 
    tptgnucmd = "plot " 
    print(len(flows))
    for i in range(len(flows)): 
        tptgnucmd += "'%s' using 1:%d with lines, " % (tptfilename, i+2) 
    tptgnufile.write(tptgnucmd) 
    tptgnufile.close 
  
    jaingnufilename = '' + idntifier + alg + '-trace' + "-jain.gnuplot" 
    jaingnufile = open(jaingnufilename, 'w') 
    jaingnufile.write(""" 
    set terminal svg; 
    set output '%s'; 
  
    set title "Dynamic behavior"; 
    set ylabel 'Jain index'; 
    set xlabel 'Time (s)'; 
    set xrange [0:%d]; 
    set yrange [0:1]; 
    set key off; 
  
    plot '%s' using 1:2 with lines 
    """ % ('' + alg + '-trace' + "-jain.svg", (num_flows*inter_flow_time*2)+delta, jainfilename)) 

    print("Run the following commands to create throughput and Jain plots.")
    print("gnuplot -p %s" % tptgnufilename) 
    print("inkscape -A %s %s" % ('' + alg + '-trace' + "-tpt.pdf", '' + alg + '-trace' + "-tpt.svg")) 
    print("gnuplot -p %s" % jaingnufilename) 
    print("inkscape -A %s %s" % ('' + alg + '-trace' + "-jain.pdf", '' + alg + '-trace' + "-jain.svg")) 
  

print("preparing to generate CDF plot")
sleep(10) #pause to make sure data is written before trying to graph it
jains = [] 
  
names = {'markovian': 'Copa', 'cubic': 'Cubic', 'bbr': 'BBR', 'pcc': 'PCC',
       'reno': 'Reno', 'vegas': 'Vegas'} 
colors = {'markovian': 'purple', 'cubic': 'green', 'bbr': 'blue', 'pcc': 'goldenrod',
          'reno': 'red', 'vegas': 'black'} 
for alg in algs: 
    with open(idntifier+ alg + '-trace-jain.dat', 'r') as f: 
        for line in f: 
            data = line.split(' ')
            if(float(data[0]) <= num_flows*inter_flow_time*2 + delta):
                jains.append(float(data[1])) 
  
    print(alg + " median jain index: " + str(np.median(np.array(jains)))) 
    plt.hist(jains, bins = 50, normed=True, cumulative=True, histtype='step',  
        color=colors[alg], alpha=0.55, label = names[alg]) 
  
plt.xlabel('Jain Index') 
plt.ylabel('CDF') 
plt.legend(loc='upper left') 
plt.show() 