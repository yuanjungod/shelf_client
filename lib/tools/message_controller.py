import Queue
import time
import threading
from device.proto.gateway  import device_gateway_pb2_grpc
from device.proto.gateway  import device_gateway_pb2
from lib import any_pb2
import logging
import json
import traceback


class MessageController(object):

    def __init__(self, channel, shelf, response_queue, client_config, online=True):
        self._channel = channel
        self._shelf = shelf
        self._request_queue = Queue.Queue()
        self._response_queue = response_queue
        self.client_config = client_config
        self._wait_for_confirm_msg = dict()
        self.scan_start = None
        self.online = online
        threading.Thread(target=self.simulation).start()

    def simulation(self):
        any = any_pb2.Any()
        any.Pack(device_gateway_pb2.MessageCreateDeviceToken(device_token="hehehe"))
        code_used = device_gateway_pb2.StreamMessage(
            id=str(time.time()), payload=any)

        any = any_pb2.Any()
        any.Pack(device_gateway_pb2.MessageUnlockDoor())
        unlock = device_gateway_pb2.StreamMessage(
            id=str(time.time()), payload=any)
        event_list = [device_gateway_pb2.AuthorizationRequest()]
        for event in event_list:
            time.sleep(5)
            logging.debug("$$$$$$$$$$$$event$$$$$$$$$$$$$$$$$$$: %s" % type(event))
            self._request_queue.put(event)

    def process_request(self):
        while True:
            request = self._request_queue.get()
            if request == "shelf_init":
                self._shelf.process_request(request)
            elif hasattr(request, "reply_to") and request.reply_to != "":
                if request.reply_to in self._wait_for_confirm_msg:
                    self._wait_for_confirm_msg.pop(request.reply_to)
            elif request.SerializeToString().find("AliyunFederationTokenRequest") != -1:
                stub = device_gateway_pb2_grpc.DeviceGatewayStub(self._channel)
                ali_token = stub.AliyunFederationToken(request)
                self._shelf.aliyun.set_aliyun(ali_token)
            else:
                self._shelf.process_request(request)

    def create_response_iterator(self):
        while True:
            try:
                if not self._shelf.camera.return_cmd_queue.empty():
                    self._response_queue.put(self._shelf.camera.return_cmd_queue.get())
                if self._response_queue.empty():
                    if self._shelf.shelf_current_info is not None and \
                            self._shelf.shelf_current_info["expires_time"] < time.time() and self._shelf.in_use is False:
                        self._response_queue.put(device_gateway_pb2.AuthorizationRequest())

                    for key, value in self._wait_for_confirm_msg.items():
                        if time.time() - value["timestamp"] > 5:
                            self._wait_for_confirm_msg[key]["timestamp"] = time.time()
                            yield value["response"]
                    time.sleep(0.5)
                    continue
                else:
                    response = self._response_queue.get(timeout=0.5)

                logging.info("create_response_iterator: %s" % type(response))
                logging.info("create_response_iterator: %s" % dir(response))
                # if response == "shelf_init":
                #     pass
                # elif response.SerializeToString().find("StreamMessage") != -1:
                #     logging.info("create_response_iterator: %s" % response)
                # else:
                #     logging.info("create_response_iterator: %s" % response)
                if response == "shelf_init" or response.SerializeToString().find("StreamMessage") == -1:
                    print "fuck you!!!!"
                    # print response.SerializeToString(), type(response.SerializeToString())
                    if response == "shelf_init":
                        print "ASDFGGGGGGGGGGGGGGGGGG"
                        self._request_queue.put(response)
                        continue 
                    elif response.SerializeToString().find("AuthorizationRequest") != -1:
                        stub = device_gateway_pb2_grpc.DeviceGatewayStub(self._channel)
                        authorization_info = stub.Authorization(response)
                        print "qwertyuiop"
                        print "#$$#$#$#$#$#$#$#$#$#$#$###$#", authorization_info.code.code != u""
                        # logging.info(len(authorization_info.code))

                        if authorization_info.code.code != "":
                            print "authorization_info"
                            self._shelf.shelf_current_info = {
                                "code": authorization_info.code.code, "qr_code": authorization_info.code.qr_code,
                                "expires_in": authorization_info.code.expires_in, "shelf_id": authorization_info.shelf_id,
                                "shelf_code": authorization_info.shelf_code, "shelf_name": authorization_info.shelf_name,
                                "service_phone": authorization_info.service_phone, "success": True,
                                "expires_time": time.time()+authorization_info.code.expires_in}
                            print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&", self._shelf.shelf_current_info
                            self._shelf.shelf_display([6, self._shelf.shelf_current_info])
                        else:
                            logging.info("authorization_info: %s" % authorization_info.token.device_token)
                            self.client_config["device_token"] = authorization_info.token.device_token
                            with open("config.json", "w") as f:
                                json.dump(self.client_config, f)
                            # self._shelf.shelf_display([
                            #     4, {"device_token": authorization_info.token.device_token,
                            #         "biz_name": authorization_info.token.biz_name}])
                            self.scan_start = time.time()
                        continue
                    elif response.SerializeToString().find("AuthenticationRequest") != -1:
                        pass
                    elif response.SerializeToString().find("AliyunFederationTokenRequest") != -1:
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
                            self.client_config["device_token"] = ""
                            if self._shelf.can_serve is False:
                                self._shelf.can_serve = True
                            else:
                                self._shelf.shelf_display([2, ])
                        # yield response
                        logging.info("MessageSenseData Finished, shelf in use is: %s" % self._shelf.in_use)
                        # if message_sense_data.door_locked is False:
                        #     continue
                if response.id != "":
                    self._wait_for_confirm_msg[response.id] = {"timestamp": time.time(), "response": response}
                logging.debug(response)
                yield response
            except:
                logging.error(traceback.format_exc())

            if self._shelf.shelf_current_info is not None and \
                    self._shelf.shelf_current_info["expires_time"] < time.time() and self._shelf.in_use is False:
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


