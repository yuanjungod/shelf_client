import Queue
import time
import threading
from gateway_proto import device_gateway_pb2_grpc
from gateway_proto import device_gateway_pb2
from google.protobuf import any_pb2
import logging


class MessageController(object):

    def __init__(self, channel, shelf, response_queue, client_config):
        self._channel = channel
        self._shelf = shelf
        self._request_queue = Queue.Queue()
        self._response_queue = response_queue
        self.client_config = client_config
        self._wait_for_confirm_msg = dict()
        threading.Thread(target=self.simulation).start()

    def simulation(self):
        any = any_pb2.Any()
        any.Pack(device_gateway_pb2.MessageCodeUsed(device_token="hehehe"))
        code_used = device_gateway_pb2.StreamMessage(
            id=str(time.time()), payload=any)

        any = any_pb2.Any()
        any.Pack(device_gateway_pb2.MessageUnlockDoor())
        unlock = device_gateway_pb2.StreamMessage(
            id=str(time.time()), payload=any)
        event_list = [device_gateway_pb2.AuthorizationRequest()]
        # while True:
        for event in event_list:
            time.sleep(5)
            logging.debug("$$$$$$$$$$$$event$$$$$$$$$$$$$$$$$$$: %s" % type(event))
            self._request_queue.put(event)
        while True:
            time.sleep(60)
            self._request_queue.put(device_gateway_pb2.AuthorizationRequest())

    def process_request(self):
        while True:
            request = self._request_queue.get()
            # logging.debug("process_request: %s" % type(request))
            if hasattr(request, "reply_to") and request.reply_to != "":
                if request.reply_to in self._wait_for_confirm_msg:
                    self._wait_for_confirm_msg.pop(request.reply_to)
            elif isinstance(request, device_gateway_pb2.AliyunFederationTokenRequest):
                stub = device_gateway_pb2_grpc.DeviceGatewayStub(self._channel)
                ali_token = stub.AliyunFederationToken(request)
                self._shelf.aliyun.set_aliyun(ali_token)
            else:
                self._shelf.process_request(request)

    def create_response_iterator(self):
        while True:
            try:
                # logging.debug("waiting for response_queue")
                if not self._shelf.camera.return_cmd_queue.empty():
                    self._response_queue.put(self._shelf.camera.return_cmd_queue.get())
                response = self._response_queue.get(timeout=0.5)
                if isinstance(response, device_gateway_pb2.StreamMessage):
                    logging.info("create_response_iterator: %s" % response.payload.type_url)
                else:
                    logging.info("create_response_iterator: %s" % response)
                if not isinstance(response, device_gateway_pb2.StreamMessage):
                    if isinstance(response, device_gateway_pb2.AuthorizationRequest):
                        stub = device_gateway_pb2_grpc.DeviceGatewayStub(self._channel)
                        authorization_info = stub.Authorization(response)
                        # print authorization_info
                        self._shelf.shelf_current_info = {
                            "code": authorization_info.code, "qr_code": authorization_info.qr_code,
                            "expires_in": authorization_info.expires_in, "shelf_id": authorization_info.shelf_id,
                            "shelf_code": authorization_info.shelf_code, "shelf_name": authorization_info.shelf_name,
                            "service_phone": authorization_info.service_phone, "success": 1,
                            "expires_time": time.time()+authorization_info.expires_in}
                        self._shelf.shelf_display([6, self._shelf.shelf_current_info])
                        continue
                    elif isinstance(response, device_gateway_pb2.AuthenticationRequest):
                        pass
                    elif isinstance(response, device_gateway_pb2.AliyunFederationTokenRequest):
                        logging.info("AliyunFederationTokenRequest")
                        stub = device_gateway_pb2_grpc.DeviceGatewayStub(self._channel)
                        ali_token = stub.AliyunFederationToken(response)
                        self._shelf.aliyun.set_aliyun(ali_token)
                        continue
                    elif response == "shelf_init":
                        self._request_queue.put(response)
                        continue
                else:
                    if response.payload.type_url.find("MessageSenseData") != -1:
                        logging.info("MessageSenseData")
                        message_sense_data = device_gateway_pb2.MessageSenseData()
                        response.payload.Unpack(message_sense_data)
                        if message_sense_data.door_locked is True and self._shelf.camera.working == 0:
                            self._shelf.in_use = False
                            self.client_config["device_token"] = ""
                            if self._shelf.can_serve is False:
                                self._shelf.can_serve = True
                            else:
                                self._shelf.shelf_display([2, ])
                        yield response
                        logging.info("MessageSenseData Finished, shelf in use is: %s" % self._shelf.in_use)
                        if message_sense_data.door_locked is False:
                            continue
                if response.id != "":
                    self._wait_for_confirm_msg[response.id] = {"timestamp": time.time(), "response": response}
                yield response
            except:
                pass
            if self._shelf.shelf_current_info is not None and self._shelf.shelf_current_info["expires_time"] < time.time():
                self._response_queue.put(device_gateway_pb2.AuthorizationRequest())

            for key, value in self._wait_for_confirm_msg.items():
                if time.time() - value["timestamp"] > 5:
                    self._wait_for_confirm_msg[key]["timestamp"] = time.time()
                    yield value["response"]

    def stream_start(self):
        stub = device_gateway_pb2_grpc.DeviceGatewayStub(self._channel)

        response_iterator = self.create_response_iterator()

        for request in stub.Stream(response_iterator):
            logging.info(request)
            self._request_queue.put(request)

    def run(self):
        process_request = threading.Thread(target=self.process_request)
        process_request.start()
        self.stream_start()
        logging.error("*******************stream end ****************")


