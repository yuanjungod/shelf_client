#!/usr/bin/env bash


echo "ml frame server start" >> /home/gxm/code/shelf_client/test.tex
pid=`ps -ef | grep "/home/gxm/code/ML_framework_express" | grep -v "grep" | awk -F \  {'print $2'}`
if [ "$pid" = "" ] ; then
cd /home/gxm/code/ML_framework_express/
git pull origin matser
cp -rf /home/gxm/code/ML_framework_express/lib /home/gxm/code/ML_framework_express/env/lib/python2.7/site-packages/
cp -rf /home/gxm/code/ML_framework_express/models /home/gxm/code/ML_framework_express/env/lib/python2.7/site-packages/
nohup /home/gxm/code/ML_framework_express/env/bin/python /home/gxm/code/ML_framework_express/offline_server_run.py &
# rm -rf *.log
fi
echo "ml frame server finished" >> /home/gxm/code/shelf_client/test.tex


echo "image server start" >> /home/gxm/code/shelf_client/test.tex
pid=`ps -ef | grep "python -m SimpleHTTPServer 8888" | grep -v "grep" | awk -F \  {'print $2'}`
if [ "$pid" = "" ] ; then
cd /home/gxm/code/shelf_client
nohup python -m SimpleHTTPServer 8888 &
# rm -rf *.log
fi
echo "fucking finished" >> /home/gxm/code/shelf_client/test.tex


export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:.
chmod 666 /dev/parport0
chmod 666 /dev/ttyS0
echo "client start" >> /home/gxm/code/shelf_client/test.tex
pid=`ps -ef | grep "/home/gxm/code/shelf_client/env/bin/python /home/gxm/code/shelf_client" | grep -v "grep" | awk -F \  {'print $2'}`
if [ "$pid" = "" ] ; then
cd /home/gxm/code/shelf_client/
git pull origin dev
cp -rf /home/gxm/code/shelf_client/lib /home/gxm/code/shelf_client/env/lib/python2.7/site-packages/
cp -rf /home/gxm/code/shelf_client/device_back /home/gxm/code/shelf_client/env/lib/python2.7/site-packages/device
nohup /home/gxm/code/shelf_client/env/bin/python /home/gxm/code/shelf_client/client.py &
echo "client running" >> /home/gxm/code/shelf_client/test.tex
# rm -rf *.log
fi





