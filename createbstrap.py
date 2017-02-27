#!/usr/bin/python
#This script is used to generate bstraplist for scality nodes.It take file /etc/ringhosts as input to generate bstraplist for the specific host dynamically.
#blame: Vipin Narayanan (vipin_narayanan@cable.comcast.com)

import random
import os
infile = "/etc/ringhosts"
bstrapfile = "/etc/bstraplist"
hostname = os.popen('hostname -s').read()
hostid = os.popen('hostname -s|cut -d- -f3|cut -c2-3').read()
no_of_nodes = 6

def createbstrap(hostid):
  hostlist = open(infile,"r")
  no_of_hosts = len(hostlist.readlines())
  no_of_bstrap = no_of_hosts // no_of_nodes 
  bstraplist = open(bstrapfile,"w")
  bt_seq = 0
  output = 'none'
  for bt_no in range(1, no_of_bstrap): 
    list = ""
    for l_no in range(bt_no, no_of_hosts, no_of_bstrap):
       host = open(infile,"r").readlines()[l_no]
       list = list + host.strip() + ":port,"
    for port in range(4244, 4250):
       bt_seq += 1
       if bt_seq <= 9:
          bstrap = "bstrap" + "0" + str(bt_seq)
       else:
          bstrap = "bstrap" + str(bt_seq)
       bstrap = bstrap.strip() + ":" + list.replace("port" , str(port)).rstrip(",") 
       bstraplist.write(bstrap + '\n')
       if bt_seq == hostid and bstrap.find(hostname.strip()) == -1:
          output = bstrap
  bstraplist.close()
  hostlist.close()
  return bt_seq,output

hostid = int(hostid)
x = 1
while True:
  x += 1
  id,bstrap = createbstrap(hostid)
  if bstrap is not 'none':
    print bstrap
    break
  else:
    hostid = id / x 
#end
