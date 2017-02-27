#!/usr/bin/python
import io
import os
import re
import sys
from yaml import load

time = os.popen('date +%s').read().strip()
source = os.popen('hostname').read().strip()

def format_it(**metrics):
  result = ''
  for metric in metrics:
    if metrics[metric]['tst'] == 'lt':
      if metrics[metric]['data'] < metrics[metric]['warn']:
         severity = 'OK:'
      elif metrics[metric]['data'] < metrics[metric]['crit']:
         severity = 'WARNING:'
      else:
         severity = 'CRITICAL:'
    elif metrics[metric]['tst'] == 'gt':
      if metrics[metric]['data'] > metrics[metric]['warn']:
         severity = 'OK:'
      elif metrics[metric]['data'] > metrics[metric]['crit']:
         severity = 'WARNING:'
      else:
         severity = 'CRITICAL:'
    for word in metrics[metric]['of'].split(':'):
      if word == '$severity$':
         result = str(result) + severity
      elif word == '$data$':
         result = str(result) + str(metrics[metric]['data'])
      elif word == '$time$':
         result = str(result) + str(time)
      elif word == '$source$':
         result = str(result) + source
      elif word == '$metric$':
         result = str(result) + metric
      elif word == '$warn$':
         result = str(result) + str(metrics[metric]['warn'])
      elif word == '$crit$':
         result = str(result) + str(metrics[metric]['crit'])
      else:
         result = result + word
    result = result + '\n'
  return result

def main():
  for conf in load(file(sys.argv[1], 'r')):
    for log in conf:
      offset = '/tmp/logmonofset_' + os.path.basename(log)
      try:
        of_set = open(offset,"r").readline()
        of_set = int(of_set)
        if os.stat(log).st_size < of_set:
           of_set = 1
      except IOError:
           of_set = 1
      with io.open(log, 'r') as stream:
        stream.seek(of_set)
        metrics = {}
        for metric in conf[log]:
           metrics[metric] = {}
           metrics[metric]['warn'] = conf[log][metric]['warn']
           metrics[metric]['crit'] = conf[log][metric]['crit']
           metrics[metric]['tst'] = conf[log][metric]['tst']
           metrics[metric]['of'] = conf[log][metric]['outformat']
           metrics[metric]['data'] = 0
        while 1:
          line = stream.readline()
          if not line:
            of_set = stream.tell()
            open(offset,"w").write(str(of_set))
            break
          for metric in conf[log]:
            p = re.compile(conf[log][metric]['grepat'])
            if p.match(line):
               match = 'y'
               for pattern in conf[log][metric]['ex_pat'].split():
                   p = re.compile(pattern)
                   if p.match(line):
                      match = 'n'
               if match == 'y':
                  metrics[metric]['data'] = metrics[metric]['data'] + 1
        print format_it(**metrics).strip() 

if __name__ == "__main__":
   main()
