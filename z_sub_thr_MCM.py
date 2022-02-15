# Copyright (c) 2017, 2020 ADLINK Technology Inc.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# http://www.eclipse.org/legal/epl-2.0, or the Apache License, Version 2.0
# which is available at https://www.apache.org/licenses/LICENSE-2.0.
#
# SPDX-License-Identifier: EPL-2.0 OR Apache-2.0
#
# Contributors:
#   ADLINK zenoh team, <zenoh@adlink-labs.tech>

import sys
import time
from datetime import datetime,timedelta
import argparse
import json
import zenoh
import os
import re
import hashlib
from zenoh import  Reliability, SubMode

# --- Command line argument parsing --- --- --- --- --- ---
parser = argparse.ArgumentParser(
    prog='z_sub_thr',
    description='zenoh throughput sub example')
parser.add_argument('--mode', '-m', dest='mode',
                    choices=['peer', 'client'],
                    type=str,
                    help='The zenoh session mode.')
parser.add_argument('--peer', '-e', dest='peer',
                    metavar='LOCATOR',
                    action='append',
                    type=str,
                    help='Peer locators used to initiate the zenoh session.')
parser.add_argument('--listener', '-l', dest='listener',
                    metavar='LOCATOR',
                    action='append',
                    type=str,
                    help='Locators to listen on.')
parser.add_argument('--samples', '-s', dest='samples',
                    default=10000,
                    metavar='NUMBER',
                    action='append',
                    type=int,
                    help='Number of throughput measurements.')
parser.add_argument('--number', '-n', dest='number',
                    default=10,
                    metavar='NUMBER',
                    action='append',
                    type=int,
                    help='Number of messages in each throughput measurements.')
parser.add_argument('--key', '-k', dest='key',
                    default='/demo/example/**',
                    type=str,
                    help='The key expression to subscribe to.')
parser.add_argument('--config', '-c', dest='config',
                    metavar='FILE',
                    type=str,
                    help='A configuration file.')

args = parser.parse_args()
conf = zenoh.config_from_file(args.config) if args.config is not None else zenoh.Config()
if args.mode is not None:
    conf.insert_json5("mode", json.dumps(args.mode))
if args.peer is not None:
    conf.insert_json5("peers", json.dumps(args.peer))
if args.listener is not None:
    conf.insert_json5("listeners", json.dumps(args.listener))
m = args.samples
n = args.number
key = args.key
print(m)
print(n)
# zenoh-net code  --- --- --- --- --- --- --- --- --- --- ---


def print_stats(id):
    stop = datetime.now()
    #print("{:.6f} msgs/sec".format(n / (stop - start).total_seconds()))
    #print(">> [Subscriber] Received {})".format(id))
    #print(size[int(id)])
    #print(stop)
    #print(start[int(id)])
    #print((stop - start[int(id)]).total_seconds())
    print("{:.6f} M bytes/sec".format((size[int(id)]/(1024*1024)) / (stop - start[int(id)]).total_seconds()))
    p=createfolder('D:\\examples\\data\\',id)
    now = teststart.strftime("%Y_%m_%d_%H_%M_%S_%f")
    f = open(p+'\\throughput_'+str(id)+'_'+str(now)+'.txt','a')
    f.write("{:.6f}\n".format((size[int(id)]/(1024*1024)) / (stop - start[int(id)]).total_seconds()))
    f.close()

thrcount=[0]*8
teststart=None
substart = None
pubstart=None
now=None
nm = 0
size=[0]*8
start=[None]*8
lastdataindex=[0]*8
def Checdataloss(data,id):
    j_data={}
    j_data=json.loads(data)
    if (j_data['dataindex']-lastdataindex[int(id)])!=1:
       print(j_data['dataindex']-lastdataindex[int(id)]) 
       print('ID :'+id+' loss data')
       p=createfolder('D:\\examples\\data\\',id)
       now = teststart.strftime("%Y_%m_%d_%H_%M_%S_%f")
       f = open(p+'\\dataloss_'+str(id)+'_'+str(now)+'.txt','a')
       f.write(str(j_data['dataindex'])+' '+str(lastdataindex[int(id)]))      
       f.close()
    checkmd5=j_data['md5']
    rawdata=j_data['payload']
    if j_data['md5']!=hashlib.md5(j_data['payload'].encode('utf-8')).hexdigest():
       print('ID :'+id+' data content is wrong')
       p=createfolder('D:\\examples\\data\\',id)
       now = teststart.strftime("%Y_%m_%d_%H_%M_%S_%f")
       f = open(p+'\\datawrong_'+str(id)+'_'+str(now)+'.txt','a')
       f.write(j_data['md5']+' '+hashlib.md5(j_data['payload'].encode('utf-8')).hexdigest())      
       f.close()
    lastdataindex[int(id)]=j_data['dataindex']

        
def Checdlatency(substarttime,pubstarttime,id):       
     now = teststart.strftime("%Y_%m_%d_%H_%M_%S_%f")
     p=createfolder('D:\\examples\\data\\',id)
     f = open(p+'\\overlatency_'+str(id)+'_'+str(now)+'.txt','a')
     f.write('{:.6f}\n'.format((substarttime-pubstarttime).total_seconds()))
     f.close()

def createfolder(folderpath,id):    
    if not os.path.exists(folderpath+str(id)):    
     os.makedirs(folderpath+str(id))
     #os.chmod(folderpath+str(id),0o777)
    path=folderpath+str(id)
    return path

def listener(sample):
#    print(">> [Subscriber] Received {})"
#          .format(sample.key_expr))
    global n, m, nm ,size,f,now,substart ,pubstart,sourceid
    sourceid=''.join(re.findall('[0-9]',str(sample.key_expr)))
    ctime = '(not specified)' if sample.source_info is None or sample.timestamp is None else datetime.fromtimestamp(
    sample.timestamp.time)
    pubstart=ctime
    if thrcount[int(sourceid)] == 0: 
        start[int(sourceid)] = datetime.now()
        substart=start[int(sourceid)] 
    elif thrcount[int(sourceid)] < n:               
        substart = datetime.now()        
    else:
        print_stats(sourceid)
        nm += 1
        thrcount[int(sourceid)] = -1
        size[int(sourceid)]=0    
    Checdataloss(sample.payload,sourceid)   
    Checdlatency(substart,pubstart,sourceid)
    size[int(sourceid)] += sys.getsizeof(sample.payload)
    print(size[int(sourceid)])
    thrcount[int(sourceid)] +=1

    
# initiate logging
zenoh.init_logger()

session = zenoh.open(conf)

rid = session.declare_expr(key)#('/test/thr')
teststart=datetime.now()
sub = session.subscribe(rid, listener, reliablity=Reliability.Reliable, mode=SubMode.Push)

print("Enter 'q' to quit...")
c = '\0'
while c != 'q':
    c = sys.stdin.read(1)
    if c == '':
        time.sleep(1)

#time.sleep(600)
for i in range(8):
  print(lastdataindex[i])


session.undeclare_expr(rid)
session.close()
