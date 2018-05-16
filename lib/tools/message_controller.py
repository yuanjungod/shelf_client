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
        any.Pack(device_gateway_pb2.MessageRevokeDeviceToken())
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
            # time.sleep(30)
            # self._request_queue.put(code_used)

    def process_request(self):
        while True:
            request = self._request_queue.get()
            if hasattr(request, "reply_to") and request.reply_to != "":
                if request.reply_to in self._wait_for_confirm_msg:
                    logging.debug("reply to: %s"%request.reply_to)
                    self._wait_for_confirm_msg.pop(request.reply_to)
            elif request == "shelf_init":
                self._shelf.process_request(request)
            elif str(type(request)).find("AliyunFederationTokenRequest") != -1:
                stub = device_gateway_pb2_grpc.DeviceGatewayStub(self._channel)
                ali_token = stub.AliyunFederationToken(request)
                self._shelf.aliyun.set_aliyun(ali_token)
            else:
                logging.debug("shelf process %s" % request)
                self._shelf.process_request(request)

    def create_response_iterator(self):
        while True:
            try:
                if not self._shelf.camera.return_cmd_queue.empty():
                    self._response_queue.put(self._shelf.camera.return_cmd_queue.get())
                if self._response_queue.empty():
                    time.sleep(2)
                    if self._shelf.shelf_current_info is not None and \
                            self._shelf.shelf_current_info["expires_time"] < time.time() and self._shelf.in_use is False:
                        self._response_queue.put(device_gateway_pb2.AuthorizationRequest())
                        self._response_queue.put(device_gateway_pb2.StreamMessage())
                        logging.debug("time for AuthorizationRequest")
                    if self._shelf.in_use is False and self._shelf.camera.working == 0:
                        self._shelf.light.auto_check()
                    # for key, value in self._wait_for_confirm_msg.items():
                    #     if time.time() - value["timestamp"] > 20:
                    #         self._wait_for_confirm_msg[key]["timestamp"] = time.time()
                    #         logging.debug(value["response"])
                    #         yield value["response"]
                else:
                    response = self._response_queue.get(timeout=0.5)
                    logging.debug(response)

                    if str(type(response)).find("StreamMessage") == -1:
                        logging.info("create_response_iterator: %s" % type(response))
                    else:
                        logging.info(response.payload.type_url)

                    if response == "shelf_init" or str(type(response)).find("StreamMessage") == -1:
                        logging.debug("fuck you!!!!")
                        # print response.SerializeToString(), type(response.SerializeToString())
                        if response == "shelf_init":
                            logging.debug("ASDFGGGGGGGGGGGGGGGGGG")
                            self._request_queue.put(response)
                            continue
                        elif str(type(response)).find("AuthorizationRequest") != -1:
                            logging.debug("qwertyuiop")
                            stub = device_gateway_pb2_grpc.DeviceGatewayStub(self._channel)
                            authorization_info = stub.Authorization(response, timeout=5)
                            logging.debug("Authorization end %s" % authorization_info)
                            logging.debug("#$$#$#$#$#$#$#$#$#$#$#$###$# %s" % authorization_info.code.code != u"")
                            # logging.info(len(authorization_info.code))

                            if authorization_info.code.code != "":
                                logging.debug("authorization_info")
                                self._shelf.shelf_current_info = {
                                    "code": authorization_info.code.code, "qr_code": authorization_info.code.qr_code,
                                    "expires_in": authorization_info.code.expires_in, "shelf_id": authorization_info.shelf_id,
                                    "shelf_code": authorization_info.shelf_code, "shelf_name": authorization_info.shelf_name,
                                    "service_phone": authorization_info.service_phone, "success": True,
                                    "expires_time": time.time()+authorization_info.code.expires_in}
                                logging.debug("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&", self._shelf.shelf_current_info)
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
                        elif str(type(response)).find("AuthenticationRequest") != -1:
                            pass
                        elif str(type(response)).find("AliyunFederationTokenRequest") != -1:
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
                            # yield response
                            logging.info("MessageSenseData Finished, shelf in use is: %s" % self._shelf.in_use)
                            # if message_sense_data.door_locked is False:
                            #     continue
                    if response.id != "":
                        self._wait_for_confirm_msg[response.id] = {"timestamp": time.time(), "response": response}
                    logging.debug(response)
                    yield response
                    continue
            except:
                logging.error(traceback.format_exc())

    def stream_start(self):
        stub = device_gateway_pb2_grpc.DeviceGatewayStub(self._channel)

        response_iterator = self.create_response_iterator()

        for request in stub.Stream(response_iterator):
            # logging.info(type(request))
            logging.info(request)
            self._request_queue.put(request)

    def run(self):
        process_request = threading.Thread(target=self.process_request)
        process_request.start()
        self.stream_start()
        logging.error("*******************stream end ****************")


