export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:.
sudo chmod 666 /dev/parport0
sudo chmod 666 /dev/ttyS0
ps -ef|grep "sudo nohup python client.py"|awk '{print $2}'|while read pid
    do
       sudo kill -9 $pid
    done
rm -rf debug.log
sudo nohup python client.py &
