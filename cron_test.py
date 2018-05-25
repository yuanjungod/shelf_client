import time
import sys
sys.path.append("/home/gxm/code/shelf_client")
from lib import device_gateway_pb2, device_gateway_pb2_grpc


count = 25

while count > 0:
    time.sleep(2)
