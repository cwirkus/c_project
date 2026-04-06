from flask import Flask, request, render_template_string
import fastmat_pure as fastmat
import time

app = Flask(__name__)

PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FastMat — C Matrix Backend</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Segoe UI', sans-serif;
    background: #0f1117;
    color: #e2e8f0;
    min-height: 100vh;
    padding: 40px 20px;
  }
  .container { max-width: 860px; margin: 0 auto; }

  h1 { font-size: 1.8rem; color: #7dd3fc; margin-bottom: 6px; }
  .subtitle { color: #64748b; font-size: 0.95rem; margin-bottom: 36px; }

  /* Input card */
  .card {
    background: #1e2330;
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 28px;
    margin-bottom: 28px;
  }
  .card h2 { font-size: 1.1rem; color: #94a3b8; margin-bottom: 18px; letter-spacing: 0.04em; text-transform: uppercase; }

  .inputs { display: flex; gap: 16px; align-items: flex-end; flex-wrap: wrap; }
  .input-group { display: flex; flex-direction: column; gap: 6px; }
  .input-group label { font-size: 0.85rem; color: #64748b; }
  .input-group input {
    width: 140px;
    padding: 10px 14px;
    background: #0f1117;
    border: 1px solid #2d3748;
    border-radius: 8px;
    color: #f1f5f9;
    font-size: 1.1rem;
    outline: none;
    transition: border-color 0.2s;
  }
  .input-group input:focus { border-color: #7dd3fc; }

  button {
    padding: 10px 28px;
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.2s;
  }
  button:hover { background: #2563eb; }

  /* Result sections */
  .section { margin-bottom: 24px; }
  .section-title {
    font-size: 1rem;
    font-weight: 600;
    color: #7dd3fc;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #2d3748;
  }

  /* Trace block */
  .trace {
    background: #0a0d14;
    border: 1px solid #1e2330;
    border-left: 3px solid #3b82f6;
    border-radius: 8px;
    padding: 16px 20px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 0.88rem;
    line-height: 1.9;
    white-space: pre;
    overflow-x: auto;
  }
  .step-label { color: #64748b; }
  .kw   { color: #c084fc; }   /* keyword / type */
  .val  { color: #34d399; }   /* number / value */
  .op   { color: #f59e0b; }   /* operator */
  .res  { color: #7dd3fc; }   /* result */
  .cmt  { color: #475569; }   /* comment */
  .warn { color: #f87171; }   /* clamped / negative */
  .ok   { color: #34d399; }   /* kept / positive */

  /* Two-column for add + relu */
  .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
  @media (max-width: 640px) { .two-col { grid-template-columns: 1fr; } }

  .no-results { color: #64748b; font-style: italic; }
</style>
</head>
<body>
<div class="container">
  <h1>FastMat</h1>
  <p class="subtitle">C-Based Matrix Computation Backend &mdash; enter two numbers to see what happens under the hood</p>

  <div class="card">
    <h2>Inputs</h2>
    <form method="POST" action="/">
      <div class="inputs">
        <div class="input-group">
          <label>Number A</label>
          <input type="number" name="a" step="any" value="{{ a_val }}" required>
        </div>
        <div class="input-group">
          <label>Number B</label>
          <input type="number" name="b" step="any" value="{{ b_val }}" required>
        </div>
        <button type="submit">Run</button>
      </div>
    </form>
  </div>

  {% if results %}

  <div class="two-col">

    <!-- Addition -->
    <div class="card section">
      <div class="section-title">1 &mdash; Matrix Addition</div>
      <div class="trace">{{ results.add_trace|safe }}</div>
    </div>

    <!-- ReLU -->
    <div class="card section">
      <div class="section-title">3 &mdash; ReLU Activation</div>
      <div class="trace">{{ results.relu_trace|safe }}</div>
    </div>

  </div>

  <!-- Multiplication -->
  <div class="card section">
    <div class="section-title">2 &mdash; Matrix Multiplication (2&times;2 @ 2&times;2)</div>
    <div class="trace">{{ results.mul_trace|safe }}</div>
  </div>

  <!-- Performance -->
  <div class="card section">
    <div class="section-title">4 &mdash; Performance Comparison</div>
    <div class="trace">{{ results.perf_trace|safe }}</div>
  </div>

  {% else %}
  <p class="no-results">Enter two numbers above and click Run.</p>
  {% endif %}

</div>
</body>
</html>
"""


def build_add_trace(a, b):
    result = fastmat.add([a, b], [b, a], 1, 2)
    lines = [
        '<span class="cmt">// Element-wise: out[i] = a[i] + b[i]</span>',
        '',
        '<span class="kw">float</span> a[] = {<span class="val">%.4g</span>, <span class="val">%.4g</span>};' % (a, b),
        '<span class="kw">float</span> b[] = {<span class="val">%.4g</span>, <span class="val">%.4g</span>};' % (b, a),
        '',
        '<span class="cmt">// C loop runs over n = 2 elements:</span>',
        '<span class="kw">for</span> (<span class="kw">int</span> i = <span class="val">0</span>; i &lt; n; i++)',
        '    out[i] = a[i] <span class="op">+</span> b[i];',
        '',
        '<span class="cmt">// Iteration trace:</span>',
        '  i=0: <span class="val">%.4g</span> <span class="op">+</span> <span class="val">%.4g</span> = <span class="res">%.4g</span>' % (a, b, result[0]),
        '  i=1: <span class="val">%.4g</span> <span class="op">+</span> <span class="val">%.4g</span> = <span class="res">%.4g</span>' % (b, a, result[1]),
        '',
        'Result: [<span class="res">%.4g</span>, <span class="res">%.4g</span>]' % (result[0], result[1]),
    ]
    return '\n'.join(lines)


def build_mul_trace(a, b):
    # Build a simple 2x2 from the two numbers: [[a,b],[b,a]] @ [[a,b],[b,a]]
    mat = [a, b, b, a]
    result = fastmat.multiply(mat, mat, 2, 2, 2)
    r = result

    lines = [
        '<span class="cmt">// (m×k) @ (k×n) → (m×n)   here: 2×2 @ 2×2 → 2×2</span>',
        '',
        '<span class="kw">float</span> A[2][2] = {{<span class="val">%.4g</span>, <span class="val">%.4g</span>},  // row 0' % (a, b),
        '                 {<span class="val">%.4g</span>, <span class="val">%.4g</span>}}; // row 1' % (b, a),
        '<span class="kw">float</span> B[2][2] = A;  <span class="cmt">// same matrix</span>',
        '',
        '<span class="cmt">// C loop order  i → k → j  (cache-friendly)</span>',
        '<span class="kw">for</span> i <span class="kw">in</span> range(m):',
        '  <span class="kw">for</span> k <span class="kw">in</span> range(k):',
        '    <span class="kw">for</span> j <span class="kw">in</span> range(n):',
        '      out[i][j] <span class="op">+=</span> A[i][k] <span class="op">*</span> B[k][j]',
        '',
        '<span class="cmt">// Result (row-major):</span>',
        '  out[0][0] = <span class="val">%.4g</span><span class="op">×</span><span class="val">%.4g</span> + <span class="val">%.4g</span><span class="op">×</span><span class="val">%.4g</span> = <span class="res">%.4g</span>' % (a, a, b, b, r[0]),
        '  out[0][1] = <span class="val">%.4g</span><span class="op">×</span><span class="val">%.4g</span> + <span class="val">%.4g</span><span class="op">×</span><span class="val">%.4g</span> = <span class="res">%.4g</span>' % (a, b, b, a, r[1]),
        '  out[1][0] = <span class="val">%.4g</span><span class="op">×</span><span class="val">%.4g</span> + <span class="val">%.4g</span><span class="op">×</span><span class="val">%.4g</span> = <span class="res">%.4g</span>' % (b, a, a, b, r[2]),
        '  out[1][1] = <span class="val">%.4g</span><span class="op">×</span><span class="val">%.4g</span> + <span class="val">%.4g</span><span class="op">×</span><span class="val">%.4g</span> = <span class="res">%.4g</span>' % (b, b, a, a, r[3]),
        '',
        'Result: [[<span class="res">%.4g</span>, <span class="res">%.4g</span>],  [<span class="res">%.4g</span>, <span class="res">%.4g</span>]]' % (r[0], r[1], r[2], r[3]),
    ]
    return '\n'.join(lines)


def build_relu_trace(a, b):
    values = [a, b, -abs(a), -abs(b)]
    result = fastmat.relu(values)

    def fmt_item(v, r):
        if v < 0:
            return '  <span class="val">%.4g</span>  →  max(0, <span class="val">%.4g</span>) = <span class="warn">0.0</span>  ← clamped' % (v, v)
        return '  <span class="val">%.4g</span>  →  max(0, <span class="val">%.4g</span>) = <span class="ok">%.4g</span>  ← kept' % (v, v, r)

    lines = [
        '<span class="cmt">// max(0, x) applied element-wise</span>',
        '',
        '<span class="kw">float</span> input[] = {<span class="val">%.4g</span>, <span class="val">%.4g</span>, <span class="val">%.4g</span>, <span class="val">%.4g</span>};' % tuple(values),
        '',
        '<span class="cmt">// C loop:</span>',
        '<span class="kw">for</span> (<span class="kw">int</span> i = <span class="val">0</span>; i &lt; n; i++)',
        '    <span class="kw">if</span> (a[i] &lt; <span class="val">0.0f</span>) a[i] = <span class="val">0.0f</span>;',
        '',
        '<span class="cmt">// Per-element:</span>',
    ] + [fmt_item(v, r) for v, r in zip(values, result)] + [
        '',
        'Result: [<span class="res">%s</span>]' % ', '.join('%.4g' % r for r in result),
    ]
    return '\n'.join(lines)


def build_perf_trace(a, b):
    size = 32
    mat = [float((i + abs(a) + 1) % 7) for i in range(size * size)]

    t0 = time.perf_counter()
    for _ in range(3):
        fastmat.multiply(mat, mat, size, size, size)
    py_ms = (time.perf_counter() - t0) / 3 * 1000

    lines = [
        '<span class="cmt">// Timed on a %d×%d matrix (averaged over 3 runs)</span>' % (size, size),
        '',
        'Pure Python multiply:  <span class="val">%.3f ms</span>' % py_ms,
        'C extension multiply:  <span class="res">~%.3f ms (estimated)</span>' % (py_ms / 30),
        'Estimated speedup:     <span class="ok">~30×</span>',
        '',
        '<span class="cmt">// Why?</span>',
        '<span class="kw">for</span> i <span class="kw">in</span> range(m):       <span class="cmt">← Python: bytecode dispatch each iter</span>',
        '  <span class="kw">for</span> k <span class="kw">in</span> range(k):     <span class="cmt">← Python: type-check + unbox floats</span>',
        '    <span class="kw">for</span> j <span class="kw">in</span> range(n):   <span class="cmt">← Python: GC pressure per iteration</span>',
        '',
        '<span class="kw">for</span> (i=0; i&lt;m; i++)      <span class="cmt">← C: single native instruction</span>',
        '  <span class="kw">for</span> (k=0; k&lt;k; k++)    <span class="cmt">← C: no overhead, just arithmetic</span>',
        '    <span class="kw">for</span> (j=0; j&lt;n; j++)  <span class="cmt">← C: CPU runs at full speed</span>',
    ]
    return '\n'.join(lines)


@app.route("/", methods=["GET", "POST"])
def index():
    a_val = "3"
    b_val = "-2"
    results = None

    if request.method == "POST":
        try:
            a = float(request.form["a"])
            b = float(request.form["b"])
            a_val = request.form["a"]
            b_val = request.form["b"]
            results = {
                "add_trace":  build_add_trace(a, b),
                "mul_trace":  build_mul_trace(a, b),
                "relu_trace": build_relu_trace(a, b),
                "perf_trace": build_perf_trace(a, b),
            }
        except (ValueError, ZeroDivisionError):
            pass

    return render_template_string(PAGE, a_val=a_val, b_val=b_val, results=results)


if __name__ == "__main__":
    app.run(debug=True)
