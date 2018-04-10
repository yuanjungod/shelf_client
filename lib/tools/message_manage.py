#  -*- coding:utf-8 -*- 
import Queue
import time
import threading
from example import device_gateway_pb2, device_gateway_pb2_grpc


class MessageManage(object):

    def __init__(self, channel, shelf, response_queue):
        self._channel = channel
        self._shelf = shelf
        self._request_queue = Queue.Queue()
        self._response_queue = response_queue
        self._wait_for_confirm_msg = dict()

    def add_request_queue(self, request):
        self._request_queue.put(request)

    def process_request(self):
        while True:
            request = self._request_queue.get()
            if request.ReplyId != "":
                if request.ReplyId in self._wait_for_confirm_msg:
                    self._wait_for_confirm_msg.pop(request.ReplyId)
            else:
                self._response_queue.put(self._shelf.execute_server_command(request))

    def add_response_queue(self, response):
        self._response_queue.put(response)

    def create_response_iterator(self):
        while True:
            try:
                response = self._response_queue.get(timeout=1)
                if response.id != "":
                    self._wait_for_confirm_msg[response.id] = {
                        "timestamp": time.time(),
                        "response": response
                    }
                if response.door_status == 2:
                    self._shelf.in_use = False
                yield response
            except:
                print("beat heart")
                yield device_gateway_pb2.CommandResponse()
            print "_wait_for_confirm_msg", len(self._wait_for_confirm_msg)
            for key, value in self._wait_for_confirm_msg.items():
                # print key, value
                if time.time() - value["timestamp"] > 5:
                    self._wait_for_confirm_msg[key]["timestamp"] = time.time()
                    yield value["response"]

    def process_response(self):
        stub = device_gateway_pb2_grpc.DeviceGatewayStub(self._channel)

        # while True:
        # while True:
        response_iterator = self.create_response_iterator()
        for request in stub.Command(response_iterator):
            self.add_request_queue(request)

    def run(self):
        process_request = threading.Thread(target=self.process_request)
        process_request.start()
        self.process_response()


