/*
 * fastmat.c — CPython extension module
 * Implements core matrix operations for FastMat.
 *
 * Build with:  pip install .
 *
 * Exposed Python API:
 *   fastmat.add(a, b, rows, cols)         -> list[float]
 *   fastmat.multiply(a, b, m, k, n)       -> list[float]
 *   fastmat.relu(a)                       -> list[float]
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdlib.h>
#include <string.h>

/* ── Low-level C kernels ────────────────────────────────────────────────── */

/* Element-wise addition: out[i] = a[i] + b[i] */
static void mat_add(const float *a, const float *b, float *out, int n)
{
    for (int i = 0; i < n; i++)
        out[i] = a[i] + b[i];
}

/*
 * Matrix multiplication:  out (m×n) = a (m×k)  ×  b (k×n)
 *
 * Loop order is i-k-j (rather than i-j-k) so that the inner loop
 * accesses b row-major and out row-major — both stride-1 reads/writes.
 * This is a simple but cache-friendlier layout than the naïve i-j-k order.
 */
static void mat_mul(const float *a, const float *b, float *out,
                    int m, int k, int n)
{
    memset(out, 0, (size_t)(m * n) * sizeof(float));
    for (int i = 0; i < m; i++)
        for (int p = 0; p < k; p++)
            for (int j = 0; j < n; j++)
                out[i*n + j] += a[i*k + p] * b[p*n + j];
}

/* ReLU activation: clamp negatives to zero */
static void mat_relu(float *a, int n)
{
    for (int i = 0; i < n; i++)
        if (a[i] < 0.0f) a[i] = 0.0f;
}

/* ── Conversion helpers ─────────────────────────────────────────────────── */

/* Python list[float|int] → heap-allocated float array.
   Returns NULL and sets a Python exception on error. */
static float *list_to_floats(PyObject *lst, Py_ssize_t expected_len)
{
    Py_ssize_t len = PyList_Size(lst);
    if (len != expected_len) {
        PyErr_Format(PyExc_ValueError,
                     "expected list of length %zd, got %zd",
                     expected_len, len);
        return NULL;
    }
    float *arr = (float *)malloc((size_t)len * sizeof(float));
    if (!arr) { PyErr_NoMemory(); return NULL; }

    for (Py_ssize_t i = 0; i < len; i++) {
        PyObject *item = PyList_GET_ITEM(lst, i);
        double v = PyFloat_AsDouble(item);
        if (v == -1.0 && PyErr_Occurred()) { free(arr); return NULL; }
        arr[i] = (float)v;
    }
    return arr;
}

/* heap-allocated float array → Python list[float] */
static PyObject *floats_to_list(const float *arr, int n)
{
    PyObject *lst = PyList_New(n);
    if (!lst) return NULL;
    for (int i = 0; i < n; i++)
        PyList_SET_ITEM(lst, i, PyFloat_FromDouble((double)arr[i]));
    return lst;
}

/* ── Python-callable wrapper functions ──────────────────────────────────── */

/*
 * fastmat.add(a, b, rows, cols) -> list[float]
 *
 * a, b  — flat row-major lists of length rows*cols
 */
static PyObject *py_add(PyObject *self, PyObject *args)
{
    PyObject *la, *lb;
    int rows, cols;

    if (!PyArg_ParseTuple(args, "O!O!ii",
                          &PyList_Type, &la,
                          &PyList_Type, &lb,
                          &rows, &cols))
        return NULL;

    Py_ssize_t n = (Py_ssize_t)(rows * cols);
    float *a   = list_to_floats(la, n); if (!a) return NULL;
    float *b   = list_to_floats(lb, n); if (!b) { free(a); return NULL; }
    float *out = (float *)malloc((size_t)n * sizeof(float));
    if (!out) { free(a); free(b); PyErr_NoMemory(); return NULL; }

    mat_add(a, b, out, (int)n);

    PyObject *result = floats_to_list(out, (int)n);
    free(a); free(b); free(out);
    return result;
}

/*
 * fastmat.multiply(a, b, m, k, n) -> list[float]
 *
 * a  — flat row-major list of length m*k  (shape m×k)
 * b  — flat row-major list of length k*n  (shape k×n)
 * result is flat row-major list of length m*n  (shape m×n)
 */
static PyObject *py_multiply(PyObject *self, PyObject *args)
{
    PyObject *la, *lb;
    int m, k, n;

    if (!PyArg_ParseTuple(args, "O!O!iii",
                          &PyList_Type, &la,
                          &PyList_Type, &lb,
                          &m, &k, &n))
        return NULL;

    float *a   = list_to_floats(la, (Py_ssize_t)(m * k)); if (!a) return NULL;
    float *b   = list_to_floats(lb, (Py_ssize_t)(k * n)); if (!b) { free(a); return NULL; }
    float *out = (float *)malloc((size_t)(m * n) * sizeof(float));
    if (!out) { free(a); free(b); PyErr_NoMemory(); return NULL; }

    mat_mul(a, b, out, m, k, n);

    PyObject *result = floats_to_list(out, m * n);
    free(a); free(b); free(out);
    return result;
}

/*
 * fastmat.relu(a) -> list[float]
 *
 * a — flat list of any length
 */
static PyObject *py_relu(PyObject *self, PyObject *args)
{
    PyObject *la;
    if (!PyArg_ParseTuple(args, "O!", &PyList_Type, &la))
        return NULL;

    Py_ssize_t n = PyList_Size(la);
    float *a = list_to_floats(la, n); if (!a) return NULL;

    mat_relu(a, (int)n);

    PyObject *result = floats_to_list(a, (int)n);
    free(a);
    return result;
}

/* ── Module definition ──────────────────────────────────────────────────── */

static PyMethodDef FastmatMethods[] = {
    {
        "add", py_add, METH_VARARGS,
        "add(a, b, rows, cols) -> list[float]\n\n"
        "Element-wise addition of two matrices stored as flat row-major lists."
    },
    {
        "multiply", py_multiply, METH_VARARGS,
        "multiply(a, b, m, k, n) -> list[float]\n\n"
        "Matrix multiplication: (m x k) @ (k x n) -> (m x n).\n"
        "Inputs are flat row-major lists."
    },
    {
        "relu", py_relu, METH_VARARGS,
        "relu(a) -> list[float]\n\n"
        "Apply ReLU activation: max(0, x) applied element-wise."
    },
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef fastmatmodule = {
    PyModuleDef_HEAD_INIT,
    "fastmat",
    "FastMat: C-based matrix computation backend for Python.",
    -1,
    FastmatMethods
};

PyMODINIT_FUNC PyInit_fastmat(void)
{
    return PyModule_Create(&fastmatmodule);
}
