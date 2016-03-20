from ctypes import *

class HISTROGRAM(Structure) :
    _fields_ = [
        ("k", c_uint),
        ("img_size", c_uint),
        ("cube", POINTER(c_float))
    ]

class CIMAGE(Structure) :
    _fields = [
        ("nx", c_int),
        ("ny", c_int),
        ("r", POINTER(POINTER(c_char))),
        ("g", POINTER(POINTER(c_char))),
        ("b", POINTER(POINTER(c_char)))
    ]
