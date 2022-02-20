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
import datetime
import argparse
import json
import zenoh
import random
import hashlib
import psutil
from zenoh import config, CongestionControl

# --- Command line argument parsing --- --- --- --- --- ---
parser = argparse.ArgumentParser(
    prog='z_pub_thr',
    description='zenoh throughput pub example')
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
parser.add_argument('--key', '-k', dest='key',
                    default='/demo/example/zenoh-python-pub',
                    type=str,
                    help='The key expression to publish onto.')
parser.add_argument('payload_size',
                    type=int,
                    help='Sets the size of the payload to publish.')
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
size = args.payload_size
key = args.key
# zenoh-net code  --- --- --- --- --- --- --- --- --- --- ---

# initiate logging
zenoh.init_logger()
start = None
end=None
congestion_control = CongestionControl.Block

session = zenoh.open(conf)

rid = session.declare_expr(key)

pub = session.declare_publication(rid)
totalpattern=1000
payloaddata =[]
raw=bytearray()
#for i in range(0, size):
#     raw.append(1)
for i in range(0, totalpattern):
    raw=bytearray(size)
    raw[random.randint(0,size-1)]=random.randint(0,9)
    payloaddata.append(raw)
md5=[]
for i in range(0, totalpattern):
  md5.append(hashlib.md5(payloaddata[i]).hexdigest())
  #print(md5[i])
pattern=1
print("Declaring key expression '{}'...".format(key))

while pattern <totalpattern+1:
    start = datetime.datetime.now()
    j_data = {}   
    j_data['dataindex']=pattern
    j_data['payload']=payloaddata[pattern-1].decode('utf-8')   
    j_data['md5']=md5[pattern-1]
    j_data['CPU_Usage']=psutil.cpu_percent(interval=None, percpu=False)
    j_data['RAM_Usage']=psutil.virtual_memory()[2]
    j_data['totalindex']=totalpattern
    j_data = json.dumps(j_data)
    data=bytes(j_data,encoding='utf8')  
    session.put(rid, data, congestion_control=congestion_control)
    pattern+=1    
    time.sleep(0.05)
    end= datetime.datetime.now()
#    print(end-start)
#    print(sys.getsizeof(data))
#    print(pattern)
print("Enter 'q' to quit...")
c = '\0'
while c != 'q':
    c = sys.stdin.read(1)
    if c == '':
        time.sleep(1)
