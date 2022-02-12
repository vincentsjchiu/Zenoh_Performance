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
                    default=100,
                    metavar='NUMBER',
                    action='append',
                    type=int,
                    help='Number of messages in each throughput measurements.')
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
print(m)
print(n)
# zenoh-net code  --- --- --- --- --- --- --- --- --- --- ---


def print_stats(start,id):
    stop = datetime.now()
    #print("{:.6f} msgs/sec".format(n / (stop - start).total_seconds()))
    print(size)
    print((stop - start).total_seconds())
    print("{:.6f} M bytes/sec".format((size/(1024*1024)) / (stop - start).total_seconds()))
    p=createfolder('D:\\examples\\data\\',id)
    now = teststart.strftime("%Y_%m_%d_%H_%M_%S_%f")
    f = open(p+'\\throughput.txt_'+str(now)+'.txt','a')
    f.write("{:.6f}\n".format((size/(1024*1024)) / (stop - start).total_seconds()))
    f.close()

thrcount=0
count = 0
teststart=None
substart = None
pubstart=None
now=None
nm = 0
size=0

def Checdataloss(data,index,id):    
    if index%3 ==0:
      target=1;
    elif index%3==1:
      target=2
    else:
      target=3
    for b in data:
     if b!=target:
         p=createfolder('D:\\examples\\data\\',id)
         now = teststart.strftime("%Y_%m_%d_%H_%M_%S_%f")
         print(str(now))
         f = open(p+'\\dataloss.txt_'+str(now)+'.txt','a')
         f.write(str(b)+' '+str(target)+'\n')      
         f.close()
         break
        
def Checdlatency(substarttime,pubstarttime,id):    
    if (substarttime-pubstarttime).total_seconds() >1:
         now = teststart.strftime("%Y_%m_%d_%H_%M_%S_%f")
         p=createfolder('D:\\examples\\data\\',id)
         f = open(p+'\\overlatency_'+str(now)+'.txt','a')
         f.write('{:.6f}\n'.format((substarttime-pubstarttime).total_seconds()))
         f.close()

def createfolder(folderpath,id):
    global path
    if not os.path.exists(folderpath+str(id)):    
     os.makedirs(folderpath+str(id))
     #os.chmod(folderpath+str(id),0o777)
    path=folderpath+str(id)
    return path

def listener(sample):
    global n, m, count,thrcount, start, nm ,size,f,pubstart,substart,sourceid
    if thrcount == 0:
        sourceid=1
        ctime = '(not specified)' if sample.source_info is None or sample.timestamp is None else datetime.fromtimestamp(
        sample.timestamp.time)
        pubstart=ctime
        #time.sleep(1)
        start = datetime.now()
        Checdataloss(sample.payload,count,sourceid)
        Checdlatency(start,pubstart,sourceid)
        size += sys.getsizeof(sample.payload)
        #print(putstart-start)
        #print(size)
        #f = open('C:\\examples\\data\\'+str(count)+'.txt','wb')
        #f.write(sample.payload)
        #f.close()
        count += 1
        thrcount +=1
    elif thrcount < n:       
        ctime = '(not specified)' if sample.source_info is None or sample.timestamp is None else datetime.fromtimestamp(
        sample.timestamp.time)
        pubstart=ctime
        substart = datetime.now()
        Checdataloss(sample.payload,count,sourceid)
        Checdlatency(substart,pubstart,sourceid)
        #print(substart)
        #print(putstart)
        #print(substart-putstart)
        #print(sys.getsizeof(sample.payload))
        size += sys.getsizeof(sample.payload)
        #print(sample)
        #f = open('C:\\examples\\data\\'+str(count)+'.txt','wb')
        #f.write(sample.payload)
        #f.close()
        count += 1
        thrcount +=1
        #print(count)
    else:
        print_stats(start,sourceid)
        nm += 1
        thrcount = 0
        size=0
        


# initiate logging
zenoh.init_logger()

session = zenoh.open(conf)

rid = session.declare_expr('/demo/example/zenoh-python-pub')#('/test/thr')
teststart=datetime.now()
sub = session.subscribe(rid, listener, reliablity=Reliability.Reliable, mode=SubMode.Push)

time.sleep(600)

session.undeclare_expr(rid)
session.close()
