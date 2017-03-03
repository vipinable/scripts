#!/usr/bin/python
# importing the required modules used in this script. paramiko module is used to
# access the device using ssh and string module used in the function find_fi
import paramiko
import string
# function to send the command to the device.This function is called whenever a command
# or action to be executed on a device.
def send_cmd(device,cmd):
    try:
        ssh.connect(device,username=options.uid, password=options.pwd)
    except paramiko.AuthenticationException:
        print "Invalid credentials for device %s" % (device)
        ssh.close()
    else:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.readlines()
        error = stderr.readlines()
        ssh.close()
        return output,error

# function to translate the hostname in to the respective residing fabric interconnect device name.

def find_fi(host):
  for ch in range(0,10):
    if host[11] == string.ascii_lowercase[ch]:
       ch = ch + 1
       break
    else:
       ch = 0
  bl = int(host[12])
  if bl > 8 or bl < 1:
     bl = 0
  fi = host.replace(host[10]+host[11]+host[12],'0'+host[10])
  fi = fi.replace('esx','ucsfi')
  return fi,ch,bl

# function to construct the command depending on the action specified in the command line.
# and take action on it.

def execute_cmd(device,action):

    if action == "powercycle":
            device,ch,bl = find_fi(device)
            if ch != 0 and bl != 0:
                cmd = "scope server "+str(ch)+"/"+str(bl)+";"+"show detail;reset hard-reset-immediate;commit-buffer"
                output,error = send_cmd(device,cmd)
                for line in output:
                    if 'Profile' in line:
                       print "Resetting the blade "+line.split()[2]
            else:
                print "Invalid blade"
    elif action == "poweronvms":
            output,error = send_cmd(device,'vim-cmd vmsvc/getallvms')
            for line in output:
                line = line.split()
                if len(line) != 0 and 'Vmid' not in line:
                   cmd = 'vim-cmd vmsvc/power.on '+line[0]
                   print cmd
                   print "Powering on VM:"+line[0]+":"+line[1]
    elif action == "rebootesx":
            cmd = "reboot"
            output,error = send_cmd(device,cmd)

    else:
            cmd = action
            output,error = send_cmd(device,cmd)
            for line in output:
                print ' '.join(line.split())

# reading command line opions and validating

from optparse import OptionParser
usage = "usage: %prog [options] arg"
parser = OptionParser(usage)
parser.add_option("-d", "--device", dest="device",
          help="Specify devices or hostname")
parser.add_option("-l", "--list", dest="list",
          help="Specify the filename contain list of devices or hostnames")
parser.add_option("-a", "--action", dest="action",
          help="Specify action to be performed")
parser.add_option("-u", "--user", dest="uid",
          help="Specify username")
parser.add_option("-p", "--password", dest="pwd",
          help="Specify password")
(options, args) = parser.parse_args()
if len(args) != 0:
    parser.error("Incorrect number of options, use -h or --help for available options")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

#Check whether command line specified for a single device or a list
#
#If a single device spcified using -d or --device option the command or action execute on
#the specified device only!

if options.device is not None and options.list is None:
    print options.device
    execute_cmd(options.device,options.action)

#If a list of devices specified using -l or --list command, let us iterate through the list
#and execute the action on each of the devices.

if options.device is None and options.list is not None:
    for device in open(options.list,"r"):
        print device.rstrip('\n')
        execute_cmd(device.rstrip('\n'),options.action)
#end
