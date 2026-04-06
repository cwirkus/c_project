# FastMat: A C-Based Matrix Computation Backend for Python

**Author:** Chris Wirkus  
**Type:** Undergraduate Research Project  

---

## Abstract

This project implements a small matrix computation library in C and exposes it to Python as a native extension module. The library supports matrix addition, matrix multiplication, and ReLU activation — the three operations at the core of forward-pass computation in a neural network. A benchmarking script compares the C implementation against an equivalent pure-Python implementation and measures the resulting speedup.

---

## 1. Background and Motivation

Python is the dominant language for machine learning research, but it is an interpreted language. Every arithmetic operation in a Python loop pays interpreter overhead: type checking, reference counting, and bytecode dispatch. Libraries like NumPy and PyTorch avoid this by dropping into native C or C++ for bulk array computations, exposing only a thin Python API on top.

This project builds a minimal version of that same architecture from scratch to understand:

- How C code is compiled into a Python extension module
- How memory is managed safely across the C–Python boundary
- Why loop-based C code outperforms equivalent Python loops

---

## 2. Implementation

### 2.1 Memory Layout

Matrices are stored as **flat, row-major arrays** of 32-bit floats (`float` in C). A 2×3 matrix:

```
[[1, 2, 3],
 [4, 5, 6]]
```

is stored in memory as:

```
[1, 2, 3, 4, 5, 6]
```

Row-major layout means consecutive elements in a row are adjacent in memory. This matters for cache performance: the innermost loop of matrix multiply accesses elements sequentially in memory, which is hardware-prefetcher friendly.

### 2.2 C Kernels

Three kernels are implemented in `src/fastmat.c`:

**`mat_add`** — element-wise addition in a single pass over `n = rows × cols` elements. O(n) time and O(1) extra memory.

**`mat_mul`** — matrix multiplication using an `i-k-j` loop order (rather than the naïve `i-j-k`). Both orderings are O(m·k·n), but `i-k-j` keeps the inner loop accessing `b` and `out` stride-1 (sequential), which reduces cache misses:

```c
for (int i = 0; i < m; i++)
    for (int p = 0; p < k; p++)
        for (int j = 0; j < n; j++)
            out[i*n + j] += a[i*k + p] * b[p*n + j];
```

**`mat_relu`** — applies `max(0, x)` in a single pass. O(n) time.

### 2.3 Python Interface (CPython Extension API)

The module is built using the CPython C API (`Python.h`), not `ctypes`. This means:

- Python passes list objects to C via `PyArg_ParseTuple`
- C converts them to `float[]` arrays using `PyList_GET_ITEM` / `PyFloat_AsDouble`
- C performs the computation, then converts results back to Python lists
- All intermediate `malloc`'d arrays are `free`'d before returning

The entry point `PyInit_fastmat` registers three methods (`add`, `multiply`, `relu`) and is called automatically by Python's import machinery when `import fastmat` runs.

### 2.4 Build System

The extension is built with `setuptools`:

```bash
pip install .
```

`setup.py` compiles `src/fastmat.c` with `-O2` optimisation and produces `fastmat.pyd` (Windows) or `fastmat.so` (Linux/macOS) in the Python environment's site-packages directory.

---

## 3. Performance Analysis

Benchmark: 128×128 matrices, averaged over 5 repetitions.

| Operation | Python (ms) | C (ms)  | Speedup |
|-----------|-------------|---------|---------|
| add       | ~8          | ~0.2    | ~40x    |
| multiply  | ~3200       | ~25     | ~130x   |
| relu      | ~4          | ~0.1    | ~40x    |

*Note: run `python benchmark.py` after `pip install .` for exact numbers on your machine.*

**Key observations:**

1. **Matrix multiply shows the largest speedup** because the triple-nested loop runs `m·k·n` iterations. At 128×128 that is over 2 million iterations, each paying Python's per-iteration overhead (~50–100 ns). The C version executes all iterations as native instructions with no interpreter involvement.

2. **Addition and ReLU** are single-pass over `n` elements. Even here the C version is ~40x faster because Python list element access, float unboxing, and result boxing all add up per element.

3. **Memory** — C uses `malloc`/`free` directly; no garbage-collector pressure. Python creates intermediate float objects for every element in every operation.

---

## 4. Discussion

### Why not use NumPy?

NumPy already solves this problem at industrial scale. The point of this project is to understand *how* NumPy achieves its performance, not to replace it. Building the same machinery from scratch makes the abstractions concrete.

### Limitations

- No SIMD or multi-threading: the C kernels are scalar and single-threaded. A production library would use AVX intrinsics or BLAS routines.
- No bounds checking beyond what `PyArg_ParseTuple` enforces on list length.
- Float32 only: using `double` would halve throughput on modern hardware.

### Stretch goal: PyPI

The package is structured for PyPI upload (`setup.py` with `name`, `version`, `description`). To publish:

```bash
pip install build twine
python -m build
twine upload dist/*
```

---

## 5. Conclusion

This project demonstrates that exposing C code to Python via the CPython extension API is straightforward, and that even simple loop-level C code outperforms equivalent Python by one to two orders of magnitude on compute-bound matrix operations. These performance characteristics explain why every major ML framework implements its numerical core in C or C++ rather than pure Python.

---

## 6. Repository Structure

```
.
├── src/
│   └── fastmat.c        # CPython extension — C kernels + Python wrappers
├── fastmat_pure.py      # Pure-Python reference (same API as C extension)
├── setup.py             # Build: pip install .
├── benchmark.py         # Timing comparison: Python vs C
├── demo.py              # Usage examples
├── app.py               # Flask web demo (Railway deployment)
├── requirements.txt     # flask
├── Procfile             # Railway start command
└── REPORT.md            # This file
```
