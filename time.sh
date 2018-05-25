#!/bin/sh
cd /home/gxm/code/shelf_client
echo "fucking start" >> /home/gxm/code/shelf_client/test.tex
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:.
chmod 666 /dev/parport0
chmod 666 /dev/ttyS0
pid=`ps -ef | grep "/usr/bin/python /home/gxm/code/shelf_client" | grep -v "grep" | awk -F \  {'print $2'}`
if [ "$pid" = "" ] ; then
nohup /home/gxm/code/shelf_client/env/bin/python /home/gxm/code/shelf_client/cron_test.py &
echo "running" >> /home/gxm/code/shelf_client/test.tex
# rm -rf *.log
fi
echo "fucking finished" >> /home/gxm/code/shelf_client/test.tex
