#!/bin/bash
SRC_LOG=/var/log/open-xchange/open-xchange.log.0
DST_LOG=/tmp/glm_source.log
MAX_DST_LOG_SIZE=1024000
LC=0
#Terminate if previous process running in the background
if [ -f /tmp/logconv.pid ];then
   /bin/kill -9 $(cat /tmp/logconv.pid|cut -f1)
fi
while true;do
#Start the tail command if it is not running in background
ps|grep $! > /dev/null 2>&1
if [ $? -ne 0 ];then
   DATE=$(date +%Y-%m-%d)
   /usr/bin/tail --pid=$$ -f ${SRC_LOG}|sed 's#'${DATE}'#\\'${DATE}'#g'|tr -d '\n'|tr '\\' '\n' >> ${DST_LOG} &
   /bin/ps -ef|grep -v grep|grep tail|grep $$|awk {'print $2'} > /tmp/logconv.pid
   echo $$ >> /tmp/logconv.pid
fi
LCN=$(wc /tmp/glm_source.log|awk {'print $1'})
if [ ${LCN} -eq ${LC} ];then
   /bin/kill -9 $(cat /tmp/logconv.pid|cut -f1)
   exit 1
fi
LC=$(echo ${LCN})
#Truncate the file when it cross the set max value
U=$(du ${DST_LOG}|cut -f1)
if [ ${U} -gt ${MAX_DST_LOG_SIZE} ];then
  date > ${DST_LOG}
fi
sleep 60
done
