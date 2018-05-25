#!/bin/sh
cd /home/gxm/code/shelf_client
cp -rf /home/gxm/code/shelf_client/lib /home/gxm/code/shelf_client/env/lib/python2.7/site-packages/
cp -rf /home/gxm/code/shelf_client/device /home/gxm/code/shelf_client/env/lib/python2.7/site-packages/
echo "fucking start" >> /home/gxm/code/shelf_client/test.tex
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:.
chmod 666 /dev/parport0
chmod 666 /dev/ttyS0
pid=`ps -ef | grep "/home/gxm/code/shelf_client/env/bin/python /home/gxm/code/shelf_client" | grep -v "grep" | awk -F \  {'print $2'}`
if [ "$pid" = "" ] ; then
nohup /home/gxm/code/shelf_client/env/bin/python /home/gxm/code/shelf_client/client.py &
echo "running" >> /home/gxm/code/shelf_client/test.tex
# rm -rf *.log
fi
echo "fucking finished" >> /home/gxm/code/shelf_client/test.tex
