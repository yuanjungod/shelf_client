#  -*- coding:utf-8 -*- 
import Queue


class MessageManage(object):

    def __init__(self, stub):
        self._stub = stub
        self._request_queue = Queue.Queue()
        self._responase_queue = Queue.Queue()

    def add_request_queue(self, request):
        self._request_queue.put(request)

    def add_response_queue(self, response):
        self._responase_queue.put(response)

    def response_iterator(self):
        while True:
            response = self._responase_queue.get(timeout=5)
            if response is None:
                yield ""
            yield response

    def send_response(self):
        while True:
            pass

