import sys
import ctypes

from ctypes import cdll

# Load the shared C++ library
try:
    lib_brot = cdll.LoadLibrary ("./libbrot.so")
except Exception as e:
    print(f"Failed to load C++ lib with error {e}")
    sys.exit(-1)

# Declare the arguments and types for the shared C++ function
lib_brot.generate.argtypes = [
    ctypes.c_void_p,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_ubyte)
]

# Declare the return type
lib_brot.generate.restype = None

# wrapper for the shared C++ class
class mandelbrot:
    def __init__(self):
        self.obj = lib_brot.brot_new();

    def generate(self, x, y, pitch, samples, columns, buffer):
        buf_ptr = buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))
        lib_brot.generate(self.obj, x, y, pitch, samples, columns, buf_ptr)

    def brot_delete(self):
        lib_brot.brot_delete(self.obj)
