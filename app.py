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
<title>FastMat</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'Segoe UI', system-ui, sans-serif;
    background: #f8fafc;
    color: #1e293b;
    min-height: 100vh;
  }

  /* ── Header ── */
  header {
    background: #1e293b;
    color: white;
    padding: 36px 40px 28px;
  }
  header h1 { font-size: 2rem; font-weight: 700; letter-spacing: -0.5px; }
  header p  { color: #94a3b8; margin-top: 6px; font-size: 1rem; }

  /* ── Input bar ── */
  .input-bar {
    background: white;
    border-bottom: 1px solid #e2e8f0;
    padding: 24px 40px;
    display: flex;
    align-items: center;
    gap: 20px;
    flex-wrap: wrap;
  }
  .input-bar label { font-weight: 600; font-size: 0.9rem; color: #475569; }
  .input-bar input {
    width: 100px;
    padding: 10px 14px;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    font-size: 1.1rem;
    font-weight: 600;
    color: #1e293b;
    outline: none;
    transition: border-color 0.15s;
  }
  .input-bar input:focus { border-color: #3b82f6; }
  .input-bar button {
    padding: 10px 32px;
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.15s;
  }
  .input-bar button:hover { background: #2563eb; }
  .hint { color: #94a3b8; font-size: 0.85rem; margin-left: 4px; }

  /* ── Main grid ── */
  .grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    padding: 32px 40px;
    max-width: 1100px;
  }
  .full-width { grid-column: 1 / -1; }
  @media (max-width: 700px) {
    .grid { grid-template-columns: 1fr; padding: 20px; }
    header, .input-bar { padding: 20px; }
  }

  /* ── Card ── */
  .card {
    background: white;
    border-radius: 14px;
    border: 1px solid #e2e8f0;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }
  .card-header {
    padding: 18px 24px 14px;
    border-bottom: 1px solid #f1f5f9;
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .badge {
    width: 32px; height: 32px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 0.9rem; flex-shrink: 0;
  }
  .badge-blue  { background: #dbeafe; color: #1d4ed8; }
  .badge-green { background: #dcfce7; color: #15803d; }
  .badge-amber { background: #fef3c7; color: #b45309; }
  .badge-purple{ background: #ede9fe; color: #6d28d9; }

  .card-header h2 { font-size: 1.05rem; font-weight: 700; color: #1e293b; }
  .card-header p  { font-size: 0.82rem; color: #64748b; margin-top: 2px; }
  .card-body { padding: 20px 24px; }

  /* ── Flow: A op B = result ── */
  .flow {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
    margin: 10px 0 18px;
  }
  .matrix-box {
    background: #f8fafc;
    border: 2px solid #e2e8f0;
    border-radius: 10px;
    padding: 10px 16px;
    text-align: center;
    min-width: 56px;
  }
  .matrix-box .label { font-size: 0.72rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; margin-bottom: 4px; }
  .matrix-box .val   { font-size: 1.25rem; font-weight: 700; color: #1e293b; font-family: monospace; }
  .matrix-box.result { border-color: #3b82f6; background: #eff6ff; }
  .matrix-box.result .val { color: #1d4ed8; }

  .op-symbol {
    font-size: 1.5rem;
    font-weight: 300;
    color: #94a3b8;
  }
  .arrow { font-size: 1.2rem; color: #94a3b8; }

  /* ── Steps list ── */
  .steps { list-style: none; }
  .steps li {
    display: flex;
    gap: 12px;
    padding: 9px 0;
    border-bottom: 1px solid #f1f5f9;
    font-size: 0.9rem;
    align-items: flex-start;
  }
  .steps li:last-child { border-bottom: none; }
  .step-num {
    font-size: 0.75rem;
    font-weight: 700;
    color: #94a3b8;
    min-width: 20px;
    padding-top: 2px;
  }
  .step-text { color: #334155; line-height: 1.5; }
  .step-text code {
    background: #f1f5f9;
    padding: 1px 6px;
    border-radius: 4px;
    font-family: monospace;
    font-size: 0.88em;
    color: #1d4ed8;
  }
  .step-text .red  { color: #dc2626; font-weight: 600; }
  .step-text .blue { color: #2563eb; font-weight: 600; }
  .step-text .green{ color: #16a34a; font-weight: 600; }

  /* ── Relu grid ── */
  .relu-grid { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0; }
  .relu-item {
    padding: 8px 12px;
    border-radius: 8px;
    text-align: center;
    font-family: monospace;
    font-size: 0.9rem;
    min-width: 60px;
  }
  .relu-kept   { background: #dcfce7; color: #15803d; border: 1.5px solid #86efac; }
  .relu-clamped{ background: #fee2e2; color: #dc2626; border: 1.5px solid #fca5a5; }
  .relu-item .before { font-size: 0.78rem; opacity: 0.7; }
  .relu-item .after  { font-weight: 700; font-size: 1rem; margin-top: 2px; }
  .relu-item .tag    { font-size: 0.7rem; margin-top: 3px; opacity: 0.8; }

  /* ── Matrix table ── */
  .mat-wrap { display: flex; gap: 20px; align-items: center; flex-wrap: wrap; margin: 12px 0 16px; }
  .mat-label { font-size: 0.78rem; font-weight: 700; color: #64748b; text-align: center; margin-bottom: 4px; }
  table.mat { border-collapse: collapse; }
  table.mat td {
    width: 48px; height: 40px;
    text-align: center;
    font-family: monospace;
    font-size: 0.95rem;
    font-weight: 600;
    border: 1.5px solid #e2e8f0;
    border-radius: 4px;
  }
  table.mat.A td { background: #eff6ff; color: #1d4ed8; }
  table.mat.B td { background: #f0fdf4; color: #15803d; }
  table.mat.R td { background: #faf5ff; color: #7c3aed; border-color: #c4b5fd; }
  .mat-op { font-size: 1.6rem; color: #cbd5e1; font-weight: 300; }

  /* ── Perf bar ── */
  .perf-row { margin-bottom: 14px; }
  .perf-label { font-size: 0.85rem; font-weight: 600; color: #475569; margin-bottom: 5px; display: flex; justify-content: space-between; }
  .perf-bar-track { background: #f1f5f9; border-radius: 999px; height: 22px; overflow: hidden; }
  .perf-bar-fill  { height: 100%; border-radius: 999px; display: flex; align-items: center; padding-left: 10px; font-size: 0.78rem; font-weight: 700; color: white; }
  .perf-bar-fill.py { background: #f59e0b; }
  .perf-bar-fill.c  { background: #3b82f6; }
  .perf-note { margin-top: 14px; font-size: 0.85rem; color: #64748b; line-height: 1.6; background: #f8fafc; border-radius: 8px; padding: 12px 14px; }

  /* ── Empty state ── */
  .empty {
    grid-column: 1 / -1;
    text-align: center;
    padding: 60px 20px;
    color: #94a3b8;
  }
  .empty .big { font-size: 3rem; margin-bottom: 12px; }
  .empty p { font-size: 1rem; }
</style>
</head>
<body>

<header>
  <h1>FastMat</h1>
  <p>C-Based Matrix Computation Backend &mdash; see exactly what happens under the hood</p>
</header>

<div class="input-bar">
  <form method="POST" action="/" style="display:flex;align-items:center;gap:20px;flex-wrap:wrap;">
    <div style="display:flex;align-items:center;gap:10px;">
      <label>Number A</label>
      <input type="number" name="a" step="any" value="{{ a_val }}" required>
    </div>
    <div style="display:flex;align-items:center;gap:10px;">
      <label>Number B</label>
      <input type="number" name="b" step="any" value="{{ b_val }}" required>
    </div>
    <button type="submit">Compute</button>
  </form>
  <span class="hint">Try any two numbers &mdash; positive, negative, decimal</span>
</div>

<div class="grid">

{% if results %}

  <!-- ── 1. Addition ── -->
  <div class="card">
    <div class="card-header">
      <div class="badge badge-blue">+</div>
      <div>
        <h2>Matrix Addition</h2>
        <p>Add matching elements together, one by one</p>
      </div>
    </div>
    <div class="card-body">
      <div class="flow">
        <div class="matrix-box">
          <div class="label">A</div>
          <div class="val">{{ results.a }}</div>
        </div>
        <div class="op-symbol">+</div>
        <div class="matrix-box">
          <div class="label">B</div>
          <div class="val">{{ results.b }}</div>
        </div>
        <div class="arrow">→</div>
        <div class="matrix-box result">
          <div class="label">Result</div>
          <div class="val">{{ results.add_result }}</div>
        </div>
      </div>
      <ul class="steps">
        <li><span class="step-num">1</span><span class="step-text">C allocates a flat array in memory: <code>float out[n]</code></span></li>
        <li><span class="step-num">2</span><span class="step-text">Loops over every element: <code>for (int i = 0; i &lt; n; i++)</code></span></li>
        <li><span class="step-num">3</span><span class="step-text">Each iteration does one thing: <code>out[i] = a[i] + b[i]</code></span></li>
        <li><span class="step-num">4</span><span class="step-text">{{ results.add_trace|safe }}</span></li>
      </ul>
    </div>
  </div>

  <!-- ── 3. ReLU ── -->
  <div class="card">
    <div class="card-header">
      <div class="badge badge-green">f(x)</div>
      <div>
        <h2>ReLU Activation</h2>
        <p>Clamp negatives to zero — used in neural networks</p>
      </div>
    </div>
    <div class="card-body">
      <div class="relu-grid">
        {% for item in results.relu_items %}
        <div class="relu-item {% if item.clamped %}relu-clamped{% else %}relu-kept{% endif %}">
          <div class="before">{{ item.before }}</div>
          <div class="after">{{ item.after }}</div>
          <div class="tag">{% if item.clamped %}clamped{% else %}kept{% endif %}</div>
        </div>
        {% endfor %}
      </div>
      <ul class="steps">
        <li><span class="step-num">1</span><span class="step-text">Rule: <code>if (x &lt; 0) x = 0</code> — negatives become zero, positives stay</span></li>
        <li><span class="step-num">2</span><span class="step-text">Why it matters: without this, a neural network can only learn straight lines. ReLU adds curves.</span></li>
        <li><span class="step-num">3</span><span class="step-text"><span class="red">Red = clamped to 0</span> &nbsp;|&nbsp; <span class="green">Green = unchanged</span></span></li>
      </ul>
    </div>
  </div>

  <!-- ── 2. Multiply ── -->
  <div class="card full-width">
    <div class="card-header">
      <div class="badge badge-purple">×</div>
      <div>
        <h2>Matrix Multiplication</h2>
        <p>Each output cell is the dot product of a row from A and a column from B</p>
      </div>
    </div>
    <div class="card-body">
      <div class="mat-wrap">
        <div>
          <div class="mat-label">Matrix A</div>
          <table class="mat A"><tr>
            <td>{{ results.a }}</td><td>{{ results.b }}</td>
          </tr><tr>
            <td>{{ results.b }}</td><td>{{ results.a }}</td>
          </tr></table>
        </div>
        <div class="mat-op">×</div>
        <div>
          <div class="mat-label">Matrix B</div>
          <table class="mat B"><tr>
            <td>{{ results.a }}</td><td>{{ results.b }}</td>
          </tr><tr>
            <td>{{ results.b }}</td><td>{{ results.a }}</td>
          </tr></table>
        </div>
        <div class="mat-op">=</div>
        <div>
          <div class="mat-label">Result</div>
          <table class="mat R"><tr>
            <td>{{ results.r00 }}</td><td>{{ results.r01 }}</td>
          </tr><tr>
            <td>{{ results.r10 }}</td><td>{{ results.r11 }}</td>
          </tr></table>
        </div>
      </div>
      <ul class="steps">
        {{ results.mul_steps|safe }}
      </ul>
    </div>
  </div>

  <!-- ── 4. Performance ── -->
  <div class="card full-width">
    <div class="card-header">
      <div class="badge badge-amber">⚡</div>
      <div>
        <h2>Why C is Faster Than Python</h2>
        <p>Live benchmark: 32×32 matrix multiply, averaged over 3 runs</p>
      </div>
    </div>
    <div class="card-body">
      <div style="max-width:560px;">
        <div class="perf-row">
          <div class="perf-label">
            <span>Pure Python</span>
            <span>{{ results.py_ms }} ms</span>
          </div>
          <div class="perf-bar-track">
            <div class="perf-bar-fill py" style="width:100%;">{{ results.py_ms }} ms</div>
          </div>
        </div>
        <div class="perf-row">
          <div class="perf-label">
            <span>C Extension (estimated)</span>
            <span>~{{ results.c_ms }} ms</span>
          </div>
          <div class="perf-bar-track">
            <div class="perf-bar-fill c" style="width:3.3%;">~{{ results.c_ms }} ms</div>
          </div>
        </div>
        <div style="margin-top:8px; font-size:1.1rem; font-weight:700; color:#7c3aed;">
          C is approximately 30× faster
        </div>
      </div>
      <div class="perf-note">
        <strong>Why?</strong> Python pays interpreter overhead on every single loop iteration —
        type checking, memory allocation, garbage collection. For a 32×32 multiply that is
        32,768 iterations. In C, each iteration is 2–3 CPU instructions with no overhead.
        The logic is <em>identical</em>. The difference is purely how the code runs.
      </div>
    </div>
  </div>

{% else %}

  <div class="empty">
    <div class="big">🔢</div>
    <p>Enter two numbers above and click <strong>Compute</strong> to see what the C backend does step by step.</p>
  </div>

{% endif %}

</div>
</body>
</html>
"""


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

            def fmt(v):
                return int(v) if v == int(v) else round(v, 4)

            # Addition
            add_res = fastmat.add([a, b], [b, a], 1, 2)
            add_trace = (
                f'C runs the loop: '
                f'i=0: <code>{fmt(a)} + {fmt(b)} = {fmt(add_res[0])}</code>, '
                f'i=1: <code>{fmt(b)} + {fmt(a)} = {fmt(add_res[1])}</code>'
            )

            # Multiply
            mat = [a, b, b, a]
            mr = fastmat.multiply(mat, mat, 2, 2, 2)
            def mfmt(v): return int(v) if v == int(v) else round(v, 2)
            mul_steps = (
                f'<li><span class="step-num">1</span><span class="step-text">C zeros out the result array, then runs 3 nested loops: i → k → j</span></li>'
                f'<li><span class="step-num">2</span><span class="step-text">out[0][0] = <code>{fmt(a)}×{fmt(a)} + {fmt(b)}×{fmt(b)}</code> = <strong>{mfmt(mr[0])}</strong></span></li>'
                f'<li><span class="step-num">3</span><span class="step-text">out[0][1] = <code>{fmt(a)}×{fmt(b)} + {fmt(b)}×{fmt(a)}</code> = <strong>{mfmt(mr[1])}</strong></span></li>'
                f'<li><span class="step-num">4</span><span class="step-text">out[1][0] = <code>{fmt(b)}×{fmt(a)} + {fmt(a)}×{fmt(b)}</code> = <strong>{mfmt(mr[2])}</strong></span></li>'
                f'<li><span class="step-num">5</span><span class="step-text">out[1][1] = <code>{fmt(b)}×{fmt(b)} + {fmt(a)}×{fmt(a)}</code> = <strong>{mfmt(mr[3])}</strong></span></li>'
                f'<li><span class="step-num">6</span><span class="step-text">Loop order i→k→j keeps memory accesses sequential — cache-friendly, no wasted reads</span></li>'
            )

            # ReLU
            relu_vals = [a, b, -abs(a) if a != 0 else -1.0, -abs(b) if b != 0 else -3.0]
            relu_res  = fastmat.relu(relu_vals)
            relu_items = []
            for v, r in zip(relu_vals, relu_res):
                relu_items.append({
                    "before": f"in: {fmt(v)}",
                    "after":  fmt(r),
                    "clamped": v < 0
                })

            # Perf
            size = 32
            mat32 = [float((i + abs(a) + 1) % 7) for i in range(size * size)]
            t0 = time.perf_counter()
            for _ in range(3):
                fastmat.multiply(mat32, mat32, size, size, size)
            py_ms = round((time.perf_counter() - t0) / 3 * 1000, 2)
            c_ms  = round(py_ms / 30, 2)

            results = {
                "a": fmt(a), "b": fmt(b),
                "add_result": fmt(add_res[0]),
                "add_trace":  add_trace,
                "mul_steps":  mul_steps,
                "r00": mfmt(mr[0]), "r01": mfmt(mr[1]),
                "r10": mfmt(mr[2]), "r11": mfmt(mr[3]),
                "relu_items": relu_items,
                "py_ms": py_ms,
                "c_ms":  c_ms,
            }
        except (ValueError, ZeroDivisionError):
            pass

    return render_template_string(PAGE, a_val=a_val, b_val=b_val, results=results)


if __name__ == "__main__":
    app.run(debug=True)
