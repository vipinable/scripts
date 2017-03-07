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
    int_var = 0
    cmd = cmd_prefix + ' -l runtime -s list'
    output = os.popen(cmd).read()
    for vm in output[output.find(':'):output.find('|')].lstrip(':').split(','):
      if vm:
        if 'DOWN' not in vm:
          vm = vm[:vm.find('(')].strip()
          cmd = cmd_prefix + ' -l cpu -s ready -N ' + '"' + vm + '"'
          output = os.popen(cmd).read()
          int_var = int(output[output.find('='):].split('.')[0].lstrip('=')) + int_var
    return (int_var,'cpu_ready = ' + str(int_var) + ' | cpu_ready=' + str(int_var))

  def cpu(self,cmd_prefix):
    cmd = cmd_prefix + ' -l cpu -s usage'
    output = os.popen(cmd).read()
    int_var = int(output[output.find('='):].split('.')[0].lstrip('='))
    return (int_var, 'cpu_usage = ' + str(int_var) + ' | cpu_usage=' + str(int_var))

  def mem(self,cmd_prefix):
    cmd = cmd_prefix + ' -l mem -s usage'
    output = os.popen(cmd).read()
    int_var = int(output[output.find('='):].split('.')[0].lstrip('='))
    return (int_var,'memory_usage = ' + str(int_var) + ' | memory_usage=' + str(int_var))

  def datastore(self,cmd_prefix):
    cmd = cmd_prefix + ' -l vmfs'
    output = os.popen(cmd).read()
    str_var = output[output.find(':'):output.find('|')].lstrip(':')
    int_var = None
    for vmfs in str_var.split():
      if '%' in vmfs:
        if crit > warn:
          if int_var == None or int(vmfs[1:3]) > int_var:
            int_var = int(vmfs[1:3]) 
        elif warn > crit:
          if int_var == None or int(vmfs[1:3]) < int_var:
            int_var = int(vmfs[1:3])  
        else:
            int_var = 'OK'
    return (int_var,''.join(str_var))

  def paths(self,cmd_prefix):
    cmd = cmd_prefix + ' -l storage'
    output = os.popen(cmd).read()
    state = 'OK'
    if output.split()[9].split('/')[0] != output.split()[9].split('/')[1]:
      state = 'CRITICAL'
    return (state,output.split()[9] + ' paths active')

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
    return (state,str_var)

  def iolatency(self,cmd_prefix):
    cmd = cmd_prefix + ' -l io'
    output = os.popen(cmd).read() 
    str_var = ''
    perf_var = ''
    for latency in output[:output.find('|')].replace('ms','').replace(' ','').replace('latency','_latency').split(',')[2:]: 
        str_var = str_var + ' ' + latency.replace('io','') + ', '
        perf_var = perf_var + ' ' + latency.replace('io','') + ';' + str(warn) + ';' + str(crit) +';'
    state = output.split()[1]
    return (state,str_var.rstrip(', ') + ' | ' + perf_var)

  def health(self,cmd_prefix):
    cmd = cmd_prefix + ' -l runtime'
    output = os.popen(cmd).read()      
    state = output.split()[1]
    return (state,output.split(',')[1] + ',' + output.split(',')[4])

def state(result_val,warn,crit):
  if crit > warn:
    if result_val <= warn:
      state = 'OK'
    elif result_val > warn and result_val < crit:
      state = 'WARNING'
    else:
      state = 'CRITICAL'
  else:
    if result_val >= warn:
      state = 'OK'
    elif result_val < warn and result_val > crit:
      state = 'WARNING'
    else:
      state = 'CRITICAL'
  return state

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
  parser.add_option("-w", "--warn", dest="warn",
                  help="specify warning threshould for the check")
  parser.add_option("-c", "--crit", dest="crit",
                  help="specify critial threshould for the check")
  (options, args) = parser.parse_args()

#Validate the options and handle errors
  if len(args) != 1:
    parser.error("WARNING: No argument specified")
  if not options.esxi:
    parser.error("WARNING: more options required")
#Assign default values
  crit = options.crit
  warn = options.warn
  if crit is None or warn is None:
    crit = 0
    warn = 0
#Set authenticat details
  user = 'monitor'
  paswd = 'c0mC@stM0n!t0r'

#Validate the argument and handle errors
  arg_list = ['cpuready','cpu','mem','paths','service','iolatency','health','datastore']
  if args[0] not in arg_list:
    parser.error("unknown argument")

#Create first part of perl API command 
  cmd_prefix = api + ' -H ' +  options.esxi  + ' -u ' + user + ' -p ' + paswd

#Create the class object "check"
  check = check()

#Call the specifc function in the class based on the command line argument and print the output
  try: 
    result_val,result_str = (getattr(check,args[0])(cmd_prefix))
  except:
    print "Oops! something is worng."
    exit(3)

  if type(result_val) is int:
     state = state(result_val,int(warn),int(crit))
     suffix = ';' + str(warn) + ';' + str(crit)
  else:
     state = result_val
     suffix = ''
  print state + ' - ' + result_str + suffix

  if state == 'OK':
     exit(0)
  if state == 'WARNING':
     exit(1)
  if state == 'CRITICAL':
     exit(2)
#THE END
