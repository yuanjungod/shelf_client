import time
import ctypes
import time
from ctypes import *


class Light(object):
    def __init__(self):
        self.is_open = False
        self.open_time = -1
        self.close_time = -1
        self.lib = ctypes.cdll.LoadLibrary("./libled.so")
        self.func = self.lib.LED_Board_init
        self.func.restype = c_int
        print "led init ret:"
        self.fd = self.func()
        print self.fd

    def open_light(self, led_id):
        open_func = self.lib.Open_Lights
        open_func.restype = c_int
        self.open_time = time.time()
        open_func(self.fd, led_id)

    def close_light(self, led_id):
        close_func = self.lib.Close_Lights
        close_func.restype = c_bool
        close_func(self.fd, led_id)

    def open_all_light(self):
        self.open_light(1)
        self.open_light(2)
        self.open_light(3)
        self.is_open = True
        self.open_time = time.time()

    def close_all_light(self):
        self.close_light(1)
        self.close_light(2)
        self.close_light(3)
        self.is_open = False
        self.close_time = time.time()

    # def auto_check(self):
    #     if self.is_open and time.time() - self.open_time > 300:
    #         self.close_light()


if __name__ == "__main__":
    led = Light()
    led.open_all_light()
    # led.close_light(2)


