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

# zenoh-net code  --- --- --- --- --- --- --- --- --- --- ---

# initiate logging
zenoh.init_logger()
start = None
end=None
data1 = bytearray()
for i in range(0, size):
    data1.append(1)
data1 = bytes(data1)
data2 = bytearray()
for i in range(0, size):
    data2.append(2)
data2 = bytes(data2)
data3 = bytearray()
for i in range(0, size):
    data3.append(3)
data3 = bytes(data3)
congestion_control = CongestionControl.Block

session = zenoh.open(conf)

rid = session.declare_expr('/demo/example/zenoh-python-pub')#('/test/thr')

pub = session.declare_publication(rid)
pattern=1
while True:
    if pattern%3 ==1:
     data=data1
    elif pattern%3 ==2:
     data=data2
    else: 
     data=data3
     pattern=0
     
    start = datetime.datetime.now()    
    session.put(rid, data, congestion_control=congestion_control)
    pattern+=1
    data=None
    time.sleep(0.01)
    end= datetime.datetime.now()
    #print(end-start)
