#!/usr/bin/python
#blame: Vipin Narayanan (vipin_narayanan@cable.comcast.net,vnaray001v)
#Version: 1.0 
from optparse import OptionParser
import os
import time
now = int(time.time())
spdb_node = "test2"

#Define the class with all supported functions
class show:
  def cpuperf(self,storage):
    cmd = "ssh " + storage + " statcpu -t -iter 1" 
    result = os.popen(cmd).read()
    s = "," + globals()['spdb_node'] + "," + storage + "," + args[0] + ","
    for line in result.split('\n'):
      if 'total' in line:
        print "G,idleCPU#300#raw," + str(globals()['now']) + "," + str(line.split()[3]) + s + "node" + str(line.strip()[0]) + "_cpu_idle"
        print "G,interrupts/Sec#300#raw," + str(globals()['now']) + "," + str(line.split()[4]) + s + "node" + str(line.strip()[0]) + "_cpu_intr"
        print "G,contextSwitches/Sec#300#raw," + str(globals()['now']) + "," + str(line.split()[5]) + s + "node" + str(line.strip()[0]) + "_cpu_ctxt"

  def portperf(self,storage):
    cmd = "ssh " + storage + " statport -ni -host -iter 1"
    result = os.popen(cmd).read()
    s = "," + globals()['spdb_node'] + "," + storage + "," + args[0] + ","
    for line in result.split('\n'):
      if '---' in line:
         break
      if ' t ' in line:
         line = line.strip().split()
         print "G,IOPS#300#raw," + str(globals()['now']) + "," + str(line[3]) + s + "iops_" + str(line[0]) 
         print "G,ThroughputKB/Sec#300#raw," + str(globals()['now']) + "," + str(line[6]) + s + "trupt_" + str(line[0])
         print "G,ServiceTime#300#raw," + str(globals()['now']) + "," + str(line[9]) + s + "svtime_" + str(line[0])
         print "G,QueueSize#300#raw," + str(globals()['now']) + "," + str(line[11]) + s + "iosiz_" + str(line[0])
         print "G,QueueLength#300#raw," + str(globals()['now']) + "," + str(line[13]) + s + "qlen_" + str(line[0])

  def vvperf(self,storage):
    cmd = "ssh " + storage + " statvv -ni -iter 1"
    result = os.popen(cmd).read()
    s = "," + globals()['spdb_node'] + "," + storage + "," + args[0] + ","
    for line in result.split('\n'):
      if '---' in line:
         break
      if ' t ' in line:
         line = line.strip().split()
         print "G,IOPS#300#raw," + str(globals()['now']) + "," + str(line[2]) + s + "iops_" + str(line[0])
         print "G,ThroughputKB/Sec#300#raw," + str(globals()['now']) + "," + str(line[5]) + s + "trupt_" + str(line[0])
         print "G,ServiceTime#300#raw," + str(globals()['now']) + "," + str(line[8]) + s + "svtime_" + str(line[0])
         print "G,QueueSize#300#raw," + str(globals()['now']) + "," + str(line[10]) + s + "iosiz_" + str(line[0])
         print "G,QueueLength#300#raw," + str(globals()['now']) + "," + str(line[12]) + s + "qlen_" + str(line[0])

  def memperf(self,storage):
    cmd = "ssh " + storage + " statport -ni -host -iter 1"
    result = os.popen(cmd).read()
    for line in result.split('\n'):
      if '---' in line:
         break
      print line

  def pdperf(self,storage):
    cmd = "ssh " + storage + " statpd -ni -iter 1"
    result = os.popen(cmd).read()
    s = "," + globals()['spdb_node'] + "," + storage + "," + args[0] + ","    
    for line in result.split('\n'):
      if '---' in line:
         break
      if ' t ' in line:
         line = line.strip().split()
         print "G,IOPS#300#raw," + str(globals()['now']) + "," + str(line[3]) + s + "iops_" + str(line[0])
         print "G,ThroughputKB/Sec#300#raw," + str(globals()['now']) + "," + str(line[6]) + s + "trupt_" + str(line[0])
         print "G,ServiceTime#300#raw," + str(globals()['now']) + "," + str(line[9]) + s + "svtime_" + str(line[0])
         print "G,QueueSize#300#raw," + str(globals()['now']) + "," + str(line[11]) + s + "iosiz_" + str(line[0])
         print "G,QueueLength#300#raw," + str(globals()['now']) + "," + str(line[13]) + s + "qlen_" + str(line[0])
         print "G,IdleDisk#300#raw," + str(globals()['now']) + "," + str(line[14]) + s + "idle_" + str(line[0])

  def rclperf(self,storage):
    cmd = "ssh " + storage + " statport -rcip -ni -iter 1"
    result = os.popen(cmd).read()
    s = "," + globals()['spdb_node'] + "," + storage + "," + args[0] + ","
    for line in result.split('\n'):
      if '---' in line:
         break
      if ' t ' in line:
         line = line.strip().split()
         print "G,IOPS#300#raw," + str(globals()['now']) + "," + str(line[2]) + s + "iops_" + str(line[0])
         print "G,ThroughputKB/Sec#300#raw," + str(globals()['now']) + "," + str(line[5]) + s + "truput_" + str(line[0])
         print "G,ErrorCount#300#raw," + str(globals()['now']) + "," + str(line[8]) + s + "errors_" + str(line[0])
         print "G,DropCount#300#raw," + str(globals()['now']) + "," + str(line[9]) + s + "drops_" + str(line[0])


if __name__ == "__main__":

#Define options and arguments
  usage = "usage: %prog [-s|--storage <storage fqdn> arg"
  parser = OptionParser(usage)
  parser.add_option("-s", "--storage", dest="storage",
                  help="specify the FQDN of storage")
  (options, args) = parser.parse_args()

  #Validate the options and handle errors
  if len(args) != 1:
    parser.error("WARNING: No argument specified")
  if not options.storage:
    parser.error("WARNING: more options required")

#Validate the argument and handle errors
  arg_list = ['cpuperf','memperf','portperf','vvperf','pdperf','rclperf']
  if args[0] not in arg_list:
    parser.error("unknown argument")

#Create first part of perl API command 
  cmd_prefix = 'ssh ' + options.storage

#Create the class object "check"
  show = show()
  getattr(show,args[0])(options.storage)

