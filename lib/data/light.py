import time
import ctypes
import time
from ctypes import *
import logging


class Light(object):
    def __init__(self):
        self.is_open = False
        self.open_time = -1
        self.close_time = -1
        self.lib = ctypes.cdll.LoadLibrary("./libled.so")
        self.func = self.lib.LED_Board_init
        self.func.restype = c_int
        # self.open_fd_list = [self.func() for i in range(3)]
        # self.close_fd_list = [self.func() for i in range(3)]

        logging.debug("led init ret:")

    def open_light(self, led_id):
        open_func = self.lib.Open_Lights
        open_func.restype = c_int
        fd = self.func()
        open_func(fd, led_id)

    def close_light(self, led_id):
        close_func = self.lib.Close_Lights
        close_func.restype = c_bool
        fd = self.func()
        close_func(fd, led_id)

    def open_all_light(self):
        self.open_time = time.time()
        if self.is_open is False:
            self.open_light(1)
            self.open_light(3)
            self.open_light(2)
            self.is_open = True
            time.sleep(1)

    def close_all_light(self):
        self.close_light(1)
        self.close_light(3)
        self.close_light(2)
        self.is_open = False
        self.close_time = time.time()
        time.sleep(1)

    def auto_check(self):
        if self.is_open and time.time() - self.open_time > 3000:
            self.close_all_light()


if __name__ == "__main__":
    led = Light()
    # led.open_all_light()
    led.close_all_light()


