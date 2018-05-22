#!/bin/bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:.
sudo chmod 666 /dev/parport0
sudo chmod 666 /dev/ttyS0
pid=`ps -ef | grep "sudo nohup python client.py" | grep -v "grep" | awk -F \  {'print $2'}`
if [ "$pid"x == ""x ]
then
sudo nohup python client.py &
fi
