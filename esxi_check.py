#!/usr/bin/python
#Wrapper script for esxi monitoring using nagios provided api 
#blame: Vipin Narayanan (vipin_narayanan@cable.comcast.net,vnaray001v)
#Version: 1.0 
from optparse import OptionParser
import os
api = "/usr/lib64/nagios/plugins/check_vmware_api"

#Define the class with all supported functions
class check:
  def cpuready(self,cmd_prefix):
    cmd = cmd_prefix + ' -l runtime -s list'
    output = os.popen(cmd).read()
    int_var = 0
    state = 'OK'
    for vm in output[output.find(':'):output.find('|')].lstrip(':').split(','):
      if vm:
        vm = vm[:vm.find('(')].strip()
        cmd = cmd_prefix + ' -l cpu -s ready -N ' + '"' + vm + '"'
        output = os.popen(cmd).read()
        int_var = int(output[output.find('='):].split('.')[0].lstrip('=')) + int_var
    return state + ' | cpu_ready = ' + str(int_var) + 'ms'

  def cpu(self,cmd_prefix):
    cmd = cmd_prefix + ' -l cpu -s usage'
    state = 'OK'
    output = os.popen(cmd).read()
    int_var = int(output[output.find('='):].split('.')[0].lstrip('='))
    return state + ' | cpu_usage = ' + str(int_var) + ' %'

  def mem(self,cmd_prefix):
    cmd = cmd_prefix + ' -l mem -s usage'
    state = 'OK'
    output = os.popen(cmd).read()
    int_var = int(output[output.find('='):].split('.')[0].lstrip('='))
    return state + ' | memory_usage = ' + str(int_var) + ' %'

  def paths(self,cmd_prefix):
    cmd = cmd_prefix + ' -l storage'
    state = 'OK'
    output = os.popen(cmd).read()
    if output.split()[9].split('/')[0] != output.split()[9].split('/')[1]:
      state = 'CRITICAL'
    return state + ' | ' + output.split()[9] + ' paths active'

  def service(self,cmd_prefix):
    cmd = cmd_prefix + ' -l service'
    output = os.popen(cmd).read()
    str_var = ''
    state = 'OK'
    for service in output.split(','):
      if 'TSM-SSH' in service:
        str_var = str_var + service
        if 'up' in service:
          state = 'CRITICAL'
      if 'ntpd' in service:
        str_var = str_var + service
        if 'down' in service:
          state = 'CRITICAL'
      if 'snmpd' in service:
        str_var = str_var + service
        if 'down' in service:
          state = 'CRITICAL'
    return state + ' | ' + str_var

  def iolatency(self,cmd_prefix):
    cmd = cmd_prefix + ' -l io'
    output = os.popen(cmd).read()
    state = 'OK'
    str_var = ''
    for latency in output.split(',')[2:6]: 
        str_var = str_var + latency.replace('io','').replace('=',' = ').replace('ms','') + ','     
    return state + ' |' + str_var.rstrip(',')

  def health(self,cmd_prefix):
    cmd = cmd_prefix + ' -l runtime'
    output = os.popen(cmd).read()      
    return output.split()[1] + ' |' + output.split(',')[1] + ',' + output.split(',')[4]

if __name__ == "__main__":

  try:
    open(api,'r')
  except IOError:
    print "Error: API not found, install perl API for VMware and try again"

#Define options and arguments
  usage = "usage: %prog [-H|--host <esxi fqdn> -u|--user <username> -p|--pass <password>] arg"
  parser = OptionParser(usage)
  parser.add_option("-H", "--host", dest="esxi",
                  help="specify the ESXi hostname")
  parser.add_option("-u", "--user", dest="user",
                  help="specify the username to connect ESXi")
  parser.add_option("-p", "--pass", dest="paswd",
                  help="specify the password to connect ESXi")
  (options, args) = parser.parse_args()

#Validate the options handle errors
  if len(args) != 1:
    parser.error("No argument specified")
  if not options.esxi or not options.user or not options.paswd:
    parser.error("more options required")

#Validate the argument and handle errors
  arg_list = ['cpuready','cpu','mem','paths','service','iolatency','health']
  if args[0] not in arg_list:
    parser.error("unknown argument")

#Create first part of perl API command 
  cmd_prefix = api + ' -H ' +  options.esxi  + ' -u ' + options.user + ' -p ' + options.paswd

#Create the class object "check"
  check = check()

#Call the specifc function in the class based on the command line argument and print the output
  result = (getattr(check,args[0])(cmd_prefix))
  print result
  if result.split()[0] == 'OK':
     exit(0)
  if result.split()[0] == 'WARNING':
     exit(1)
  if result.split()[0] == 'CRITICAL':
     exit(2)
#THE END
