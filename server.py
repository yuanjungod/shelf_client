# -*- coding: utf-8 -*-
import grpc
import time
from concurrent import futures
from gateway_proto import device_gateway_pb2, device_gateway_pb2_grpc


_ONE_DAY_IN_SECONDS = 60 * 60 * 24
_HOST = 'localhost'
_PORT = '50051'


class ShelfService(device_gateway_pb2_grpc.DeviceGatewayServicer):

    def Command(self, request_iterator, context):

        count = 1
        for request in request_iterator:
            print request.ReplyId == "", request.id
            if request.id != "":
                yield device_gateway_pb2.CommandRequest(ReplyId=request.id, OpendDoor=1)

            if count % 5 == 0:
                yield device_gateway_pb2.CommandRequest(id="2", OpendDoor=1)
            count += 1

    def Report(self, request, context):
        print "###############", request
        return device_gateway_pb2.CommandRequest(id="1", ChechMesage=1)

    def Authentication(self, request, context):
        print("Authentication")
        return device_gateway_pb2.AuthenticationResponse(token="fuckfuckfuckyourass", SerialNumber="121334325234234")

    def Authorization(self, request, context):
        return device_gateway_pb2.AuthorizationResponse(code="1111", qr_code="wwww", expires_in = 10)


def serve():
    grpcServer = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    device_gateway_pb2_grpc.add_DeviceGatewayServicer_to_server(ShelfService(), grpcServer)
    grpcServer.add_insecure_port(_HOST + ':' + _PORT)
    grpcServer.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        grpcServer.stop(0)


if __name__ == '__main__':
    serve()

