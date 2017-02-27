#!/bin/bash
#3Par Storage Management Utility v1.1
#Auther : Vipin N
#e-mail : vipin_narayanan@cognizant.com

#Version 1.0   :  Initial Verison
#Version 1.1   :  Added hsetcreate,hsetadd and *perf for performance data

VER=v1.1
LOG=/3parUtil/log/3parmgmt.log

TIME()
{
date "+%b%d%a%Y-%H%M"
}

#Function to show evenever user enter wrong syntax or request for help.

usage()
{
echo
echo "NAME"
echo "$0 - 3Par Storage Management Utility ${VER}"
echo
echo "Usage:"
echo "$0 [--storage <IP Address/FQDN>|--conf <configfile>|--help] [[cmd: <3par command>]|vvcreate|vvsetcreate|vvsetadd|vvexport|vvsetexport|vvunexport|vvsetunexport|hostcreate|hsetcreate|hsetadd|chperf [NoS]|memperf [NoS]|cpuperf [NoS]|iscsiperf [NoS]|ldperf [NoS]|linkperf [NoS]|pdperf  [NoS]|portperf [NoS]|qosperf [NoS]|rclperf [NoS]|rcperf [NoS]|vlunperf [NoS]|vvperf [NoS]|hostperf [NoS]]"
echo
echo "--storage <IP Address/FQDN>  : Specify the 3par Storage Management IP address or Fully qualified Domain name of the storage"
echo "--conf <configfile>          : Specify the configuration file where the list of 3Par storages are specified"
echo "--help                       : Display this output"
echo
echo "[Nos] - Number of Samples,1 to 15 are supported and 1 is default"
echo 
echo "OPTIONS"
echo
echo "hwinfo       -  Get hardware information of the storage"
echo "nodeinfo     -  Get node infomation of the storage"
echo "cpginfo      -  Get CPG information of the storage"
echo "vvinfo       -  Get avaiable Virtual Volume Information"
echo "vsetinfo     -  Get available Virtual Volume Set information"
echo "luninfo      -  Get Exported Virtual Volume information"
echo "dateinfo     -  Get date and time of the storage"
echo "hostinfo     -  Get available host information"
echo "hostsetinfo  -  Get available hostset information"
echo "vvcreate     -  Create new virtual volume"
echo "vvextend     -  Extend the size of a Virtual volume, only size increment in GB is supported"
echo "vsetcreate   -  Create new virtual volume set"
echo "vsetadd      -  Add a virtual volume to a virtual volume set"
echo "vvexport     -  Export a virtual volume to a host or hostset"
echo "hostcreate   -  Create a new host definition"
echo "hsetcreate   -  Create a new host set"
echo "hsetadd      -  Add a host to existing hostset"
echo "chperf       -  Statistics for individual chunklets"
echo "memperf      -  Statistics for cache memory pages"
echo "cpuperf      -  Statistics for CPU utilization"
echo "iscsiperf    -  Statistics for iSCSI ports"
echo "ldperf       -  Statistics for logical disks (LDs)"
echo "linkperf     -  Statistics for links (internode, pci and cache memory)"
echo "pdperf       -  Statistics for physical disks (PDs)"
echo "portperf     -  Statistics for Fibre Channel ports"
echo "qosperf      -  Statistics for QoS rules"
echo "rclperf      -  Statistics for Remote Copy links"
echo "rcperf       -  Statistics for Remote Copy volumes"
echo "vlunperf     -  Statistics for virtual volume LUN exports (VLUNs)"
echo "vvperf       -  Statistics for virtual volumes"
echo "hostperf     -  Statistics for hosts attached"
}

#Function to execute the storage commands remotely.

execute ()
{
for STORAGE in `cat /tmp/storages.$$|cut -d ":" -f1`;do

    user=`grep -w ${STORAGE} /tmp/storages.$$|cut -d ":" -f2`

    echo "Command : $*"  | tee -a ${LOG}

    input=x
    until [ ${input} = "xyes" ]||[ ${input} = "xno" ];do
    printf "Do you want to execute the above command in the storage ${STORAGE}?[yes/no]:";read input

    input=x${input}
    case ${input} in
    xyes)
       printf "===========================================================================================\n"
       printf "%-90s%-s\n"  "=${STORAGE}" "="
       printf "===========================================================================================\n"
       echo "Executing the command \"$*\"...."  | tee -a ${LOG}
       if [ `whoami` = "${user}" ];then
          ssh ${STORAGE} $*
       else
          su - ${user} -c "ssh ${STORAGE} $*"
       fi
    ;;
    xno)
       echo "User aborted" | tee -a ${LOG}
       exit 0
    ;;
    *)
       echo "Only 'yes/no' is accepted"
    esac
    done
done
}

#MAIN

#Creating a log file if doen't exist one, also recording the time of script started.

if [ ! -f ${LOG} ];then
   echo "`date`:$0 Initiated..." > ${LOG}  2>&1
else
   echo "`date`:$0 Initiated..." >> ${LOG}  2>&1
fi

#The following code is just to make sure that the user specified the required options.

if [ $# -eq 0 ]||[ -z $3 ];then
   usage
   exit 3
fi

#Checking the second option...

case ${1} in

--storage)

     ping $2 -c 2 > /dev/null 2>&1
     if [ $? -ne 0 ];then
        echo "The storage $2 is not reachable.." | tee -a ${LOG}
        exit 1
     fi

     printf "Enter the username for the storage $2:";read user
     echo "$2:${user}" > /tmp/storages.$$

;;

--conf)

     if [ -z $2 ]||[ ! -f $2 ];then
        echo "No configuration file specified or the file does not exist" | tee -a ${LOG}
        exit 1
     fi
     CONF=`echo $2`
     STORAGES=`grep -v "#" ${CONF}|cut -d ":" -f1`
     for STORAGE in `echo ${STORAGES}`;do
         ping ${STORAGE} -c 2 > /dev/null 2>&1
         if [ $? -ne 0 ];then
            echo "The storage ${STORAGE} is not reachable.." | tee -a ${LOG}
            exit 1
         fi
         VAR=`grep -w ${STORAGE} ${CONF}|cut -d ":" -f2`
         if [ -z ${VAR} ];then
            echo "No username specified for storage ${STORAGE} in configuration file ${CONF}" | tee -a ${LOG}
            exit 1
         fi
     done
     grep -v "#" ${CONF} > /tmp/storages.$$
;;

--help)
     usage
     exit 0
;;
    *)
     echo "Option ${1} is not valied"
esac


case ${3} in

cmd:)

cmd=`echo $* |cut -d ":" -f2`
if [ -z ${cmd} ];then
   echo "No command found"
   exit 0
else
   execute ${cmd}
fi

;;

vvcreate)

printf "Do you want to create thin provisioned volume?[n]/y:";read tpvv
tpvv=x${tpvv}
if [ ${tpvv} = "xy" ]||[ ${tpvv} = "xyes" ];then
   tpvv=yes
else
   tpvv=no
fi
printf "Enter the name for the new Virtual Volume:";read vv
printf "Enter the size for the volume in MB [g|G|t|T]:";read size
printf "Enter the CPG from which the User space will be allocated:";read usercpg
printf "Enter the CPG from which the snapshot space is allocated:";read snapcpg
#echo "Enter Snapshot space allocation warning in percentage:";read snapaw
#echo "Enter Snapshot space allocation limit in percentage:";read snapal
#echo "Enter User space allocation warning in percentage:";read useraw
#echo "Enter User space allocation limit in percentage:";read useral

echo "Virtual Volume Name : ${vv}"
echo "Virtual Volume Size : ${size}"
echo "Thin Provisioned : ${tpvv}"
echo "User CPG : ${usercpg}"
#echo "User CPG space allocation warning : ${useraw}"
#echo "User CPG space allocation limit : ${useral}"
echo "Snapshot CPG : ${snapcpg}"
#echo "Snapshot CPG space allocation warning : ${snapaw}"
#echo "Snapshot CPG space allocation limit : ${snapal}"
printf "Do you want to continue with above specification?[yes/no]:";read input

input=x${input}
if [ ${input} = "xyes" ];then
    if [ ${tpvv} = "yes" ];then
            cmd="createvv -tpvv -snp_cpg ${snapcpg} ${usercpg} ${vv} ${size}"
        echo $cmd
                execute ${cmd}
        fi
        if [ ${tpvv} = "no" ];then
            cmd="createvv -snp_cpg ${snapcpg} ${usercpg} ${vv} ${size}"
        echo $cmd
        execute ${cmd}
    fi
else
    echo "Only 'yes' is accepted if you want to continue"
fi

;;

vsetcreate)

VVSETNAME=""

until [ ! -z ${VVSETNAME} ] ;do
     printf "What is the name for New Virtual Volume Set?:";read VVSETNAME
     if [ -z ${VVSETNAME} ];then
        echo "Not specified a Virtual Volume Set Name"
     fi
done

cmd="createvvset ${VVSETNAME}"
execute ${cmd}

;;

vsetadd)

VVSETNAME=""
VVNAME=""

until [ ! -z ${VVSETNAME} ] && [ ! -z ${VVNAME} ] ;do
     printf "What is the Virtual Volume Name?:";read VVNAME
     printf "What is the Virtual Volume Set Name?:";read VVSETNAME
     if [ -z ${VVSETNAME} ]||[ -z ${VVNAME} ];then
        echo "Not specified a Virtual Volume or Virtual Volume Set"
     fi
done

cmd="createvvset -add ${VVSETNAME} ${VVNAME}"
execute ${cmd}

;;

vvexport)

VVNAME=""
HOSTS=""
until [ ! -z ${VVNAME} ] && [ ! -z ${HOSTS} ];do
     printf "What is the name of Virtual Volume to be exported?:";read VVNAME
     printf "What is the LUN ID?:";read LUN
     if [ -z ${LUN} ];then
        LUN=auto
     fi
     printf "Specify a host or host set:";read HOSTS
     if [ -z ${VVSETNAME} ]||[ -z ${HOSTS} ];then
        echo "Not specified a Virtual Volume or Host"
     fi
done

cmd="createvlun ${VVNAME} ${LUN} ${HOSTS}"
execute ${cmd}

;;

hostcreate)

printf "What is the host name?:";read HOST
TYPE=x
until [ ${TYPE} = "xiSCSI" ]||[ ${TYPE} = "xFC" ];do
      printf "Enter your choice, \"iSCSI\" or \"FC\" accepted:";read TYPE
      TYPE=x${TYPE}
done

   if [ ${TYPE} = xiSCSI ];then
       printf "What is the IQN of the Host?:";read IQN
   fi
   if [ ${TYPE} = xFC ];then
       printf "What is the WWPN of the Host?:";read WWPN
           WWPN=`echo ${WWPN}|sed 's/://g'`
   fi
   OSTYP=0
   until [ ${OSTYP} -eq 1 ]||[ ${OSTYP} -eq 2 ]||[ ${OSTYP} -eq 6 ]||[ ${OSTYP} -eq 7 ]||[ ${OSTYP} -eq 8 ]||[ ${OSTYP} -eq 9 ]||[ ${OSTYP} -eq 10 ]||[ ${OSTYP} -eq 11 ]||[ ${OSTYP} -eq 12 ];do
        echo "Choose your operating system type from the below"
        echo "1 Generic        Windows2003,SUSE Linux,Solaris 9/10,Xen 5.x/6.x"
        echo "2 Generic-ALUA   Solaris 11,RedHat Linux,Windows 2008/2012"
        echo "6 Generic-legacy --"
        echo "7 HPUX-legacy    VolSetAddr,Lun0SCC"
        echo "8 AIX-legacy     NACA"
        echo "9 EGENERA        SoftInq"
        echo "10 ONTAP-legacy   SoftInq"
        echo "11 VMware         SubLun,ALUA"
        echo "12 OpenVMS        UARepLun,Lun0SCC"
                printf "What is the OS running on the Host?:";read OSTYP
                if [ -z ${OSTYP} ];then
                   OSTYP=0
                fi
        done
   input=x
   until [ ${input} = "xyes" ]||[ ${input} = "xno" ];do
      printf "Do you want to add this host to an existing hostset?[yes/no]:";read input
      input=x${input}
   done

   case ${input} in

   xyes)
      printf "Host set name?:";read HOSTSET
      if [ ${TYPE} = xiSCSI ];then
         cmd="createhost -iscsi -persona ${OSTYP} ${HOST} ${IQN}"
         execute ${cmd}
         cmd="createhostset -add ${HOSTSET} ${HOST}"
         execute ${cmd}
      fi
      if [ ${TYPE} = xFC ];then
         cmd="createhost -persona ${OSTYP} ${HOST} ${WWPN}"
         execute ${cmd}
         cmd="createhostset -add ${HOSTSET} ${HOST}"
         execute ${cmd}
      fi
      ;;
   xno)
      if [ ${TYPE} = xiSCSI ];then
         cmd="createhost -iscsi -persona ${OSTYP} ${HOST} ${IQN}"
         execute ${cmd}

      fi
      if [ ${TYPE} = xFC ];then
         cmd="createhost -persona ${OSTYP} ${HOST} ${WWPN}"
         execute ${cmd}
      fi
      ;;

   *)
     echo "Your choice is case sensitive"
   esac
;;

hsetcreate)

HSETNAME=""

until [ ! -z ${HSETNAME} ] ;do
     printf "What is the name for Host Set?:";read HSETNAME
     if [ -z ${HSETNAME} ];then
        echo "Not specified a Virtual Volume Set Name"
     fi
done

cmd="createhostset ${HSETNAME}"
execute ${cmd}

;;

hsetadd)

HSETNAME=""
HNAME=""

until [ ! -z "${HSETNAME}" ] && [ ! -z "${HNAME}" ] ;do
     printf "Enter the host set name?:";read HSETNAME
	 printf "Enter the hosts in quote separated by space?:";read HNAME
     if [ -z "${HSETNAME}" ]||[ -z "${HNAME}" ];then
        echo "Not specified a host or host set"
     fi
done

for HOST in `echo ${HNAME}|tr -d '"'`;do
cmd="createhostset -add ${HSETNAME} ${HOST}"
execute ${cmd}
done

;;
hwinfo)
         cmd="showinventory"
         execute ${cmd}
;;
nodeinfo)
         cmd="shownode -verbose"
         execute ${cmd}
;;
cpginfo)
         cmd="showcpg"
         execute ${cmd}
;;
vvinfo)
         cmd="showvv"
         execute ${cmd}
;;
vsetinfo)
         cmd="showvvset -d"
         execute ${cmd}
;;
luninfo)
         cmd="showvlun"
         execute ${cmd}
;;
dateinfo)
         cmd="showdate"
         execute ${cmd}
;;
hostinfo)
         cmd="showhost -verbose"
         execute ${cmd}
;;
hostsetinfo)
         cmd="showhostset -d"
         execute ${cmd}
;;
vvextend)

while true;do
VVNAME=""
SIZE=""
until [ ! -z ${VVNAME} ] && [ ! -z ${SIZE} ];do
     printf "What is the name of Virtual Volume to be extended?:";read VVNAME
     printf "Specify the size to be incremented in GB?:";read SIZE
     if [ -z ${VVSETNAME} ]||[ -z ${SIZE} ];then
        echo "Not specified a Virtual Volume Name or Size!!"
     fi
done

cmd="growvv ${VVNAME} ${SIZE}G"
execute ${cmd}

printf "Do you want to increment size of another Virtual Volume?[yes/no]:";read ANS
if [ "${ANS}" != "yes" ];then
    echo "You are not entered 'yes' so assumes no more Virtual Volumes to extend."
    exit 0
fi
done
;;
chperf)
    SAM=`echo $* |sed 's/perf/:/g'|cut -d ":" -f2`
  	if [ -z ${SAM} ]||[ ${SAM} -lt 2 ]||[ ${SAM} -gt 15 ];then
	   #Using the default number of samples if the number of sample is not specified or specified an unsupported value.
	   SAM=1   
	fi
	cmd="statch -iter ${SAM}"
    execute ${cmd}
;;

memperf)
    SAM=`echo $* |sed 's/perf/:/g'|cut -d ":" -f2`
  	if [ -z ${SAM} ]||[ ${SAM} -lt 2 ]||[ ${SAM} -gt 15 ];then
	   #Using the default number of samples if the number of sample is not specified or specified an unsupported value.
	   SAM=1   
	fi
	cmd="statcmp -iter ${SAM}"
    execute ${cmd}
;;
cpuperf)
    SAM=`echo $* |sed 's/perf/:/g'|cut -d ":" -f2`
        if [ -z ${SAM} ]||[ ${SAM} -lt 2 ]||[ ${SAM} -gt 15 ];then
	   #Using the default number of samples if the number of sample is not specified or specified an unsupported value.
	   SAM=1   
	fi
	cmd="statcpu -t -iter ${SAM}"
    execute ${cmd}
;;
iscsiperf)
    SAM=`echo $* |sed 's/perf/:/g'|cut -d ":" -f2`
        if [ -z ${SAM} ]||[ ${SAM} -lt 2 ]||[ ${SAM} -gt 15 ];then
	   #Using the default number of samples if the number of sample is not specified or specified an unsupported value.
	   SAM=1   
	fi
	cmd="statiscsi -iter ${SAM} -prot Eth,iSCSI"
    execute ${cmd}
;;
ldperf)
    SAM=`echo $* |sed 's/perf/:/g'|cut -d ":" -f2`
        if [ -z ${SAM} ]||[ ${SAM} -lt 2 ]||[ ${SAM} -gt 15 ];then
	   #Using the default number of samples if the number of sample is not specified or specified an unsupported value.
	   SAM=1   
	fi
	cmd="statld -iter ${SAM} -ni"
    execute ${cmd}
;;
linkperf)
    SAM=`echo $* |sed 's/perf/:/g'|cut -d ":" -f2`
        if [ -z ${SAM} ]||[ ${SAM} -lt 2 ]||[ ${SAM} -gt 15 ];then
	   #Using the default number of samples if the number of sample is not specified or specified an unsupported value.
	   SAM=1   
	fi
	cmd="statlink -iter ${SAM}"
    execute ${cmd}
;;
pdperf)
    SAM=`echo $* |sed 's/perf/:/g'|cut -d ":" -f2`
        if [ -z ${SAM} ]||[ ${SAM} -lt 2 ]||[ ${SAM} -gt 15 ];then
	   #Using the default number of samples if the number of sample is not specified or specified an unsupported value.
	   SAM=1   
	fi
	cmd="statpd -iter ${SAM} -devinfo"
    execute ${cmd}
;;
portperf)
    SAM=`echo $* |sed 's/perf/:/g'|cut -d ":" -f2`
        if [ -z ${SAM} ]||[ ${SAM} -lt 2 ]||[ ${SAM} -gt 15 ];then
	   #Using the default number of samples if the number of sample is not specified or specified an unsupported value.
	   SAM=1   
	fi
	cmd="statport -iter ${SAM} -ni"
    execute ${cmd}
;; 
qosperf)
    SAM=`echo $* |sed 's/perf/:/g'|cut -d ":" -f2`
        if [ -z ${SAM} ]||[ ${SAM} -lt 2 ]||[ ${SAM} -gt 15 ];then
	   #Using the default number of samples if the number of sample is not specified or specified an unsupported value.
	   SAM=1   
	fi
	cmd="statqos -iter ${SAM}"
    execute ${cmd}
;;
rclperf)
    SAM=`echo $* |sed 's/perf/:/g'|cut -d ":" -f2`
        if [ -z ${SAM} ]||[ ${SAM} -lt 2 ]||[ ${SAM} -gt 15 ];then
	   #Using the default number of samples if the number of sample is not specified or specified an unsupported value.
	   SAM=1   
	fi
	cmd="statrcopy -iter ${SAM} -hb"
    execute ${cmd}
;;
rcperf)
    SAM=`echo $* |sed 's/perf/:/g'|cut -d ":" -f2`
        if [ -z ${SAM} ]||[ ${SAM} -lt 2 ]||[ ${SAM} -gt 15 ];then
	   #Using the default number of samples if the number of sample is not specified or specified an unsupported value.
	   SAM=1   
	fi
	cmd="statrcvv -iter ${SAM} -vvsum"
    execute ${cmd}
;;
vlunperf)
    SAM=`echo $* |sed 's/perf/:/g'|cut -d ":" -f2`
        if [ -z ${SAM} ]||[ ${SAM} -lt 2 ]||[ ${SAM} -gt 15 ];then
	   #Using the default number of samples if the number of sample is not specified or specified an unsupported value.
	   SAM=1   
	fi
	cmd="statvlun -iter ${SAM} -ni -vvsum"
    execute ${cmd}
;;
hostperf)
    SAM=`echo $* |sed 's/perf/:/g'|cut -d ":" -f2`
        if [ -z ${SAM} ]||[ ${SAM} -lt 2 ]||[ ${SAM} -gt 15 ];then
	   #Using the default number of samples if the number of sample is not specified or specified an unsupported value.
	   SAM=1   
	fi
	cmd="statvlun -iter ${SAM} -ni -hostsum"
    execute ${cmd}
;;
vvperf)
    SAM=`echo $* |sed 's/perf/:/g'|cut -d ":" -f2`
        if [ -z ${SAM} ]||[ ${SAM} -lt 2 ]||[ ${SAM} -gt 15 ];then
	   #Using the default number of samples if the number of sample is not specified or specified an unsupported value.
	   SAM=1   
	fi
	cmd="statvv -iter ${SAM} -ni"
    execute ${cmd}
;;

*)
     echo "The option ${3} is not supported"
     exit 0
esac
rm -rf /tmp/storages.$$
#END
