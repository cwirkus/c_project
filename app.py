from flask import Flask
import io, contextlib

app = Flask(__name__)

@app.route("/")
def run():
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

    inputs  = [1.0, 2.0, 3.0, 4.0, 5.0]
    targets = [1.0, 2.0, 3.0, 4.0, 5.0]
    model   = Model(learning_rate=0.01)

    output = []
    output.append("=== Before training ===")
    for x in inputs:
        output.append(f"  predict({x}) = {model.predict(x):.4f}")

    model.train(inputs, targets, epochs=200)

    output.append("\n=== After training (200 epochs) ===")
    for x in inputs:
        output.append(f"  predict({x}) = {model.predict(x):.4f}  (expected {x:.1f})")

    output.append("\n=== Generalisation (unseen values) ===")
    for x in [6.0, 10.0, 0.5]:
        output.append(f"  predict({x}) = {model.predict(x):.4f}  (expected {x})")

    return "<pre>" + "\n".join(output) + "</pre>"

if __name__ == "__main__":
    app.run()
