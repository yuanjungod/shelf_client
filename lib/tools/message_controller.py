#  -*- coding:utf-8 -*- 
import Queue
import time
import threading
from gateway_proto import device_gateway_pb2_grpc
from gateway_proto import device_gateway_pb2


class MessageController(object):

    def __init__(self, channel, shelf, response_queue):
        self._channel = channel
        self._shelf = shelf
        self._request_queue = Queue.Queue()
        self._response_queue = response_queue
        self._wait_for_confirm_msg = dict()

    def process_request(self):
        while True:
            request = self._request_queue.get()
            print "*&*^&&*^%%$%$$", request
            if hasattr(request, "reply_to") and request.reply_to != "":
                if request.reply_to in self._wait_for_confirm_msg:
                    self._wait_for_confirm_msg.pop(request.reply_to)
            elif isinstance(request, device_gateway_pb2.AliyunFederationTokenRequest):
                print "#################"
                stub = device_gateway_pb2_grpc.DeviceGatewayStub(self._channel)
                ali_token = stub.AliyunFederationToken(request)
                self._shelf.aliyun.set_aliyun(ali_token)
            else:
                self._response_queue.put(self._shelf.process_request(request))

    def create_response_iterator(self):
        while True:
            try:
                response = self._response_queue.get(timeout=0.5)
                print response, isinstance(response, device_gateway_pb2.AliyunFederationTokenRequest)

                if not isinstance(response, device_gateway_pb2.StreamMessage):
                    if isinstance(response, device_gateway_pb2.AuthorizationRequest):
                        stub = device_gateway_pb2_grpc.DeviceGatewayStub(self._channel)
                        authorization_info = stub.Authorization(response)
                        self._shelf.shelf_current_info = {
                            "code": authorization_info.code, "qr_code": authorization_info.qr_code,
                            "expires_in": authorization_info.expires_in, "shelf_id": authorization_info.shelf_id,
                            "shelf_code": authorization_info.shelf_code,
                            "shelf_name": authorization_info.shelf_name,
                            "service_phone": authorization_info.service_phone}
                        self._shelf.shelf_display([6, self._shelf.shelf_current_info])
                        continue
                    elif isinstance(response, device_gateway_pb2.AuthenticationRequest):
                        pass
                    elif isinstance(response, device_gateway_pb2.AliyunFederationTokenRequest):
                        print "#################"
                        stub = device_gateway_pb2_grpc.DeviceGatewayStub(self._channel)
                        ali_token = stub.AliyunFederationToken(response)
                        self._shelf.aliyun.set_aliyun(ali_token)
                        continue
                    elif response == "shelf_init":
                        self._request_queue.put(response)
                        continue
                else:
                    if response.payload.type_url.find("MessageSenseData") != -1:
                        yield response
                        message_sense_data = device_gateway_pb2.MessageSenseData()
                        response.payload.Unpack(message_sense_data)
                        if message_sense_data.door_locked is True and self._shelf.camera.working == 0:
                            self._shelf.in_use = False
                        if message_sense_data.door_locked is False:
                            continue
                if response.id != "":
                    self._wait_for_confirm_msg[response.id] = {"timestamp": time.time(), "response": response}
                yield response
            except:
                pass
            # print "wait_for_confirm_msg", len(self._wait_for_confirm_msg)
            for key, value in self._wait_for_confirm_msg.items():
                # print value["response"]
                if time.time() - value["timestamp"] > 5:
                    self._wait_for_confirm_msg[key]["timestamp"] = time.time()
                    yield value["response"]

    def stream_start(self):
        stub = device_gateway_pb2_grpc.DeviceGatewayStub(self._channel)

        response_iterator = self.create_response_iterator()
        for request in stub.Stream(response_iterator):
            # print request
            self._request_queue.put(request)

    def run(self):
        process_request = threading.Thread(target=self.process_request)
        process_request.start()
        self.stream_start()


