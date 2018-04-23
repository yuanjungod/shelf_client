import ctypes
from ctypes import *

lib = ctypes.cdll.LoadLibrary("./liblock.so")

func = lib.lock_init
func.restype = c_int
print "lock init ret:"
fd = func()
print fd


func = lib.open_door
func.restype = c_int
func(fd)

func = lib.getLockState
func.restype = c_bool
print "Lock Status:"
print func(fd)

func = lib.getDoorState
func.restype = c_bool
print "Door Status:"
print func(fd)

func = lib.close_door
func.restype = c_int
func

func = lib.lock_deinit
func.restype = c_int
func