"""
benchmark.py — Compare pure-Python vs C extension matrix operations.

Run after building the extension:
    pip install .
    python benchmark.py
"""

import time

import fastmat_pure as py_impl

try:
    import fastmat as c_impl
    HAS_C = True
except ImportError:
    HAS_C = False
    print("C extension not built. Run `pip install .` first.")
    print("Showing pure-Python timings only.\n")

# ── Configuration ──────────────────────────────────────────────────────────
SIZE = 128      # use 128×128 matrices
REPS = 5        # average over this many repetitions


def make_matrix(rows, cols, seed=1.0):
    """Generate a deterministic flat row-major matrix."""
    return [float(i % 7 + seed) for i in range(rows * cols)]


a = make_matrix(SIZE, SIZE, seed=1.0)
b = make_matrix(SIZE, SIZE, seed=2.0)


def time_op(fn, *args, reps=REPS):
    """Return average wall-clock time in seconds over `reps` runs."""
    # warm-up
    fn(*args)
    t0 = time.perf_counter()
    for _ in range(reps):
        fn(*args)
    return (time.perf_counter() - t0) / reps


# ── Results ────────────────────────────────────────────────────────────────
print(f"{'=' * 60}")
print(f"  FastMat Benchmark — {SIZE}×{SIZE} matrices, {REPS} reps each")
print(f"{'=' * 60}\n")

header = f"{'Operation':<14}  {'Python (ms)':>12}  {'C (ms)':>10}  {'Speedup':>9}"
print(header)
print("-" * len(header))


def row(label, py_t, c_t=None):
    py_ms = f"{py_t * 1000:.3f}"
    if c_t is not None:
        c_ms     = f"{c_t * 1000:.3f}"
        speedup  = f"{py_t / c_t:.1f}x"
    else:
        c_ms    = "n/a"
        speedup = "n/a"
    print(f"{label:<14}  {py_ms:>12}  {c_ms:>10}  {speedup:>9}")


# Addition
py_add_t = time_op(py_impl.add, a, b, SIZE, SIZE)
c_add_t  = time_op(c_impl.add,  a, b, SIZE, SIZE) if HAS_C else None
row("add", py_add_t, c_add_t)

# Multiplication
py_mul_t = time_op(py_impl.multiply, a, b, SIZE, SIZE, SIZE)
c_mul_t  = time_op(c_impl.multiply,  a, b, SIZE, SIZE, SIZE) if HAS_C else None
row("multiply", py_mul_t, c_mul_t)

# ReLU
py_relu_t = time_op(py_impl.relu, a)
c_relu_t  = time_op(c_impl.relu, a) if HAS_C else None
row("relu", py_relu_t, c_relu_t)

print()
if HAS_C:
    print("Matrix multiply is usually the biggest win because the triple-nested")
    print("loop in pure Python incurs interpreter overhead on every iteration,")
    print("while the compiled C version executes all iterations natively.")
else:
    print("Build the C extension with `pip install .` to see the speedup.")
