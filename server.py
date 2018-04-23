# -*- coding: utf-8 -*-
import grpc
import time
from concurrent import futures
from gateway_proto import device_gateway_pb2, device_gateway_pb2_grpc
from google.protobuf import any_pb2
from lib.interceptors.headers.request_header_validator_interceptor import RequestHeaderValidatorInterceptor


_ONE_DAY_IN_SECONDS = 60 * 60 * 24
_HOST = 'localhost'
_PORT = '50051'


class ShelfService(device_gateway_pb2_grpc.DeviceGatewayServicer):

    def Stream(self, request_iterator, context):
        # device_gateway_pb2.MessageUnlockDoor())
        any = any_pb2.Any()
        any.Pack(device_gateway_pb2.MessageUnlockDoor())
        # print any.PackFrom(device_gateway_pb2.MessageUnlockDoor())
        while True:
            yield device_gateway_pb2.StreamMessage(id=str(time.time()), payload=any)
            time.sleep(5)
            any = any_pb2.Any()
            any.Pack(device_gateway_pb2.MessageRefreshCode())
            yield device_gateway_pb2.StreamMessage(id=str(time.time()), payload=any)

        count = 1
        for request in request_iterator:
            # print request.ReplyId == "", request.id
            if request.id != "":
                any = any_pb2.Any()
                yield device_gateway_pb2.StreamMessage(
                    reply_to=request.id, payload=any.Pack(device_gateway_pb2.MessageUnlockDoor()))
                time.sleep(2)
                yield device_gateway_pb2.StreamMessage(
                    reply_to=request.id, payload=any.Pack(device_gateway_pb2.MessageUnlockDoor()))
                time.sleep(2)
                yield device_gateway_pb2.StreamMessage(
                    reply_to=request.id, payload=any.Pack(device_gateway_pb2.MessageUnlockDoor()))
                time.sleep(2)
                yield device_gateway_pb2.StreamMessage(
                    reply_to=request.id, payload=any.Pack(device_gateway_pb2.MessageUnlockDoor()))

            if count % 5 == 0:
                yield device_gateway_pb2.StreamMessage(id="2")
            count += 1

    def Authentication(self, request, context):
        print("Authentication")
        return device_gateway_pb2.AuthenticationReply(device_key="", device_secret="", device_token="")

    def Authorization(self, request, context):
        print("Authorization")
        return device_gateway_pb2.AuthorizationReply(
            code="", qr_code="", expires_in=1111, shelf_id="", shelf_name="", service_phone="", shelf_code="")


def serve():
    header_validator = RequestHeaderValidatorInterceptor(
        'one-time-password', '42', grpc.StatusCode.UNAUTHENTICATED, 'Access denied!')
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=(header_validator,))

    # grpcServer = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    device_gateway_pb2_grpc.add_DeviceGatewayServicer_to_server(ShelfService(), server)
    server.add_insecure_port(_HOST + ':' + _PORT)
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()

