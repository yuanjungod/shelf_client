export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:.
sudo chmod 666 /dev/parport0
sudo chmod 666 /dev/ttyS0
sudo nohup python client.py &
