import ctypes
import os

# Load the shared library
_lib_path = os.path.join(os.path.dirname(__file__), "model.dll")
_lib = ctypes.CDLL(_lib_path)

# --- Tell ctypes the argument/return types for each C function ---

_lib.create_model.argtypes = [ctypes.c_float]
_lib.create_model.restype  = ctypes.c_void_p

_lib.predict.argtypes = [ctypes.c_void_p, ctypes.c_float]
_lib.predict.restype  = ctypes.c_float

_lib.train_step.argtypes = [ctypes.c_void_p, ctypes.c_float, ctypes.c_float]
_lib.train_step.restype  = None

_lib.free_model.argtypes = [ctypes.c_void_p]
_lib.free_model.restype  = None


class Model:
    def __init__(self, learning_rate=0.01):
        self._ptr = _lib.create_model(learning_rate)

    def predict(self, x):
        return _lib.predict(self._ptr, x)

    def train(self, inputs, targets, epochs=100):
        for _ in range(epochs):
            for x, y in zip(inputs, targets):
                _lib.train_step(self._ptr, x, y)

    def __del__(self):
        if self._ptr:
            _lib.free_model(self._ptr)
            self._ptr = None
