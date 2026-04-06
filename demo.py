"""
demo.py — FastMat: C-Based Matrix Computation Backend for Python

Demonstrates matrix addition, multiplication, and ReLU activation.

Uses the compiled C extension (fastmat) if available.
Falls back to the pure-Python implementation (fastmat_pure) otherwise.

To build the C extension:
    pip install .
"""

try:
    import fastmat
    print("[Using compiled C extension]\n")
except ImportError:
    import fastmat_pure as fastmat
    print("[C extension not built — using pure Python fallback]")
    print("[Run `pip install .` to build the C extension]\n")


def fmt_matrix(flat, rows, cols):
    """Pretty-print a flat row-major list as a 2-D matrix."""
    lines = []
    for i in range(rows):
        row = [f"{flat[i*cols + j]:6.2f}" for j in range(cols)]
        lines.append("  [" + "  ".join(row) + "]")
    return "\n".join(lines)


# ── 1. Matrix Addition ─────────────────────────────────────────────────────
print("=" * 45)
print("  1. Matrix Addition  (2 × 3)")
print("=" * 45)

a = [1.0, 2.0, 3.0,
     4.0, 5.0, 6.0]

b = [7.0, 8.0,  9.0,
     10.0, 11.0, 12.0]

result = fastmat.add(a, b, 2, 3)

print("A =")
print(fmt_matrix(a, 2, 3))
print("B =")
print(fmt_matrix(b, 2, 3))
print("A + B =")
print(fmt_matrix(result, 2, 3))
print()

# ── 2. Matrix Multiplication ───────────────────────────────────────────────
print("=" * 45)
print("  2. Matrix Multiplication  (2×3) @ (3×2)")
print("=" * 45)

c = [1.0, 2.0, 3.0,
     4.0, 5.0, 6.0]          # 2×3

d = [7.0,  8.0,
     9.0,  10.0,
     11.0, 12.0]              # 3×2

result = fastmat.multiply(c, d, 2, 3, 2)   # → 2×2

print("A (2×3) =")
print(fmt_matrix(c, 2, 3))
print("B (3×2) =")
print(fmt_matrix(d, 3, 2))
print("A @ B (2×2) =")
print(fmt_matrix(result, 2, 2))
print("Expected:")
print("  [[ 58.00   64.00]")
print("   [139.00  154.00]]")
print()

# ── 3. ReLU Activation ────────────────────────────────────────────────────
print("=" * 45)
print("  3. ReLU Activation")
print("=" * 45)

e = [-3.0, -1.0, 0.0, 1.5, 2.0, -0.5, 4.0, -2.2]
result = fastmat.relu(e)

print(f"Input  = {e}")
print(f"Output = {result}")
print("(All negative values clamped to 0.0)")
