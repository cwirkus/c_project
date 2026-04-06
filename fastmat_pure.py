"""
fastmat_pure.py — Pure-Python reference implementation of the fastmat API.

Matches the interface of the compiled C extension exactly so that any code
importing fastmat can fall back to this module without changes.

Matrices are represented as flat, row-major lists of floats.
A 2×3 matrix [[1,2,3],[4,5,6]] is stored as [1,2,3,4,5,6].
"""


def add(a, b, rows, cols):
    """Element-wise addition of two matrices.

    Args:
        a, b  : flat row-major lists of length rows*cols
        rows  : number of rows
        cols  : number of columns

    Returns:
        New list of length rows*cols with a[i]+b[i] for each element.
    """
    n = rows * cols
    return [a[i] + b[i] for i in range(n)]


def multiply(a, b, m, k, n):
    """Matrix multiplication: (m×k) @ (k×n) → (m×n).

    Args:
        a  : flat row-major list of length m*k
        b  : flat row-major list of length k*n
        m  : rows in a
        k  : cols in a / rows in b
        n  : cols in b

    Returns:
        Flat row-major list of length m*n.
    """
    out = [0.0] * (m * n)
    for i in range(m):
        for p in range(k):
            for j in range(n):
                out[i*n + j] += a[i*k + p] * b[p*n + j]
    return out


def relu(a):
    """Apply ReLU activation: max(0, x) element-wise.

    Args:
        a : flat list of floats (any shape)

    Returns:
        New list with negative values clamped to 0.
    """
    return [x if x > 0.0 else 0.0 for x in a]
