"""
Demo: train a linear model on y = x.

Tries to use the compiled C library (model.dll / model.so) first.
Falls back to a pure-Python implementation if the library isn't built yet.
"""

import os, sys

USE_C = os.path.exists("model.dll") or os.path.exists("model.so")

if USE_C:
    from model import Model
    print("[Using compiled C library]\n")
else:
    print("[C library not built — using pure Python fallback]")
    print("[Run `python build.py` after installing gcc to use the C version]\n")

    class Model:
        def __init__(self, learning_rate=0.01):
            self.weight        = 0.0
            self.bias          = 0.0
            self.learning_rate = learning_rate

        def predict(self, x):
            return x * self.weight + self.bias

        def train(self, inputs, targets, epochs=100):
            for _ in range(epochs):
                for x, y in zip(inputs, targets):
                    error        = y - self.predict(x)
                    self.weight += self.learning_rate * error * x
                    self.bias   += self.learning_rate * error


# --- Dataset: y = x ---
inputs  = [1.0, 2.0, 3.0, 4.0, 5.0]
targets = [1.0, 2.0, 3.0, 4.0, 5.0]

model = Model(learning_rate=0.01)

print("=== Before training ===")
for x in inputs:
    print(f"  predict({x}) = {model.predict(x):.4f}")

model.train(inputs, targets, epochs=200)

print("\n=== After training (200 epochs) ===")
for x in inputs:
    print(f"  predict({x}) = {model.predict(x):.4f}  (expected {x:.1f})")

print("\n=== Generalisation (unseen values) ===")
for x in [6.0, 10.0, 0.5]:
    print(f"  predict({x}) = {model.predict(x):.4f}  (expected {x})")
