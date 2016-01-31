from ctypes import *

class HISTROGRAM(Structure) :
    _fields_ = [
        ("k" , c_uint),
        ("img_size", c_uint),
        ("cube", POINTER(c_float))
    ]
