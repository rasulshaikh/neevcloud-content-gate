import os
import yaml
import streamlit as st
from gate.gate import QualityGate
from gate.corpus import Post, parse_markdown

st.set_page_config(
    page_title="NeevCloud Content Gate",
    page_icon="🛡",
    layout="wide",
)

# Color system (GitHub dark palette - proven contrast ratios)
# base #0D1117 | surface #161B22 | border #484F58
# text-1 #E6EDF3 | text-2 #8B949E | accent #22C55E

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Reset ── */
html, body, .stApp { font-family: 'Inter', sans-serif !important; }
.stApp { background: #0D1117 !important; }
#MainMenu, footer, [data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }
.block-container { padding-top: 1.5rem !important; max-width: 1160px !important; }

/* ── Inputs - simple selectors that always work ── */
input, input[type="text"], input[type="search"] {
    background: #161B22 !important;
    border: 1px solid #484F58 !important;
    border-radius: 6px !important;
    color: #E6EDF3 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
}
input:focus, input[type="text"]:focus {
    border-color: #22C55E !important;
    box-shadow: 0 0 0 3px rgba(34,197,94,0.15) !important;
    outline: none !important;
}
textarea {
    background: #161B22 !important;
    border: 1px solid #484F58 !important;
    border-radius: 6px !important;
    color: #8B949E !important;
    font-family: 'SF Mono', 'Fira Code', monospace !important;
    font-size: 12px !important;
    line-height: 1.65 !important;
}
textarea:focus {
    border-color: #22C55E !important;
    box-shadow: 0 0 0 3px rgba(34,197,94,0.15) !important;
    outline: none !important;
}

/* ── Input labels ── */
.stTextInput label, .stTextArea label, .stSelectbox label {
    color: #8B949E !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background: #161B22 !important;
    border: 1px solid #484F58 !important;
    border-radius: 6px !important;
    color: #E6EDF3 !important;
}
[data-testid="stSelectbox"] svg { fill: #8B949E !important; }
[data-baseweb="popover"] { background: #161B22 !important; border: 1px solid #484F58 !important; }

/* ── Button ── */
.stButton > button {
    background: linear-gradient(135deg, #22C55E 0%, #16A34A 100%) !important;
    color: #052E16 !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    letter-spacing: 0.2px !important;
    border: none !important;
    border-radius: 7px !important;
    padding: 13px 28px !important;
    box-shadow: 0 0 0 1px rgba(34,197,94,0.3), 0 4px 20px rgba(34,197,94,0.2) !important;
    transition: box-shadow 0.2s ease, transform 0.15s ease !important;
    cursor: pointer !important;
    font-family: 'Inter', sans-serif !important;
}
.stButton > button:hover {
    box-shadow: 0 0 0 1px rgba(34,197,94,0.5), 0 6px 28px rgba(34,197,94,0.4) !important;
    transform: translateY(-1px) !important;
}

/* ── Divider ── */
.nc-hr { border: none; border-top: 1px solid #21262D; margin: 18px 0; }

/* ── Header ── */
.nc-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 16px 0 20px; border-bottom: 1px solid #21262D; margin-bottom: 22px;
}
.nc-logo { display: flex; align-items: center; gap: 13px; }
.nc-logo-icon {
    width: 38px; height: 38px; border-radius: 9px; flex-shrink: 0;
    background: linear-gradient(135deg, #22C55E 0%, #15803D 100%);
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 0 20px rgba(34,197,94,0.3);
}
.nc-title { font-size: 17px; font-weight: 700; color: #E6EDF3; letter-spacing: -0.3px; }
.nc-sub { font-size: 12px; color: #6E7681; margin-top: 2px; }
.nc-live {
    display: flex; align-items: center; gap: 7px;
    background: #0A1F0F; border: 1px solid rgba(34,197,94,0.3);
    color: #4ADE80; font-size: 11px; font-weight: 600;
    padding: 5px 12px; border-radius: 20px; letter-spacing: 0.4px;
}
.nc-dot {
    width: 7px; height: 7px; background: #22C55E; border-radius: 50%;
    box-shadow: 0 0 7px #22C55E; display: inline-block;
}

/* ── Stats ── */
.nc-stats {
    display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin-bottom: 24px;
}
.nc-stat {
    background: #161B22; border: 1px solid #30363D; border-radius: 9px;
    padding: 15px 18px; position: relative; overflow: hidden;
}
.nc-stat::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: var(--ac, #30363D);
}
.nc-stat-v { font-size: 26px; font-weight: 800; letter-spacing: -1px; line-height: 1; }
.nc-stat-l { font-size: 10px; color: #6E7681; font-weight: 600; margin-top: 5px;
             text-transform: uppercase; letter-spacing: 0.9px; }
.g { color: #22C55E; } .b { color: #58A6FF; }

/* ── Section label ── */
.nc-lbl {
    font-size: 10px; font-weight: 700; color: #6E7681; text-transform: uppercase;
    letter-spacing: 1.1px; margin-bottom: 9px; display: flex; align-items: center; gap: 8px;
}
.nc-lbl::after { content: ''; flex: 1; height: 1px; background: #21262D; }

/* ── Verdict ── */
.nc-v {
    border-radius: 10px; padding: 20px 24px; margin: 6px 0 20px;
    display: flex; align-items: center; gap: 18px;
}
.nc-v-pass { background: #0A1F0F; border: 1px solid rgba(34,197,94,0.4);
             box-shadow: 0 0 32px rgba(34,197,94,0.07); }
.nc-v-flag { background: #1A1300; border: 1px solid rgba(245,158,11,0.4);
             box-shadow: 0 0 32px rgba(245,158,11,0.07); }
.nc-v-fail { background: #1A0606; border: 1px solid rgba(248,81,73,0.4);
             box-shadow: 0 0 32px rgba(248,81,73,0.07); }
.nc-v-ico {
    width: 52px; height: 52px; border-radius: 10px; display: flex;
    align-items: center; justify-content: center; font-size: 24px;
    font-weight: 800; flex-shrink: 0;
}
.nc-v-pass .nc-v-ico { background: rgba(34,197,94,0.12); color: #22C55E; }
.nc-v-flag .nc-v-ico { background: rgba(245,158,11,0.12); color: #F59E0B; }
.nc-v-fail .nc-v-ico { background: rgba(248,81,73,0.12); color: #F85149; }
.nc-v-body { flex: 1; }
.nc-v-status { font-size: 24px; font-weight: 800; letter-spacing: -0.6px; line-height: 1; }
.nc-v-pass .nc-v-status { color: #3FB950; }
.nc-v-flag .nc-v-status { color: #D29922; }
.nc-v-fail .nc-v-status { color: #F85149; }
.nc-v-desc { font-size: 13px; margin-top: 4px; }
.nc-v-pass .nc-v-desc { color: rgba(63,185,80,0.65); }
.nc-v-flag .nc-v-desc { color: rgba(210,153,34,0.65); }
.nc-v-fail .nc-v-desc { color: rgba(248,81,73,0.65); }
.nc-v-score { text-align: right; flex-shrink: 0; }
.nc-v-score-n { font-size: 32px; font-weight: 800; letter-spacing: -1px;
                line-height: 1; color: #30363D; }
.nc-v-score-l { font-size: 10px; color: #484F58; text-transform: uppercase;
                letter-spacing: 0.9px; margin-top: 3px; font-weight: 600; }

/* ── Check grid ── */
.nc-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 11px; margin-top: 4px; }
.nc-card {
    background: #161B22; border: 1px solid #30363D; border-radius: 9px; padding: 14px 15px;
}
.nc-card-pass { border-color: rgba(63,185,80,0.25); }
.nc-card-flag { border-color: rgba(210,153,34,0.3); }
.nc-card-fail { border-color: rgba(248,81,73,0.3); }
.nc-card-h { display: flex; align-items: center; justify-content: space-between; margin-bottom: 9px; }
.nc-card-n { font-size: 12px; font-weight: 600; color: #8B949E; }
.nc-chip { font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 4px; letter-spacing: 0.7px; }
.nc-chip-pass { background: rgba(63,185,80,0.1); color: #3FB950; border: 1px solid rgba(63,185,80,0.2); }
.nc-chip-flag { background: rgba(210,153,34,0.1); color: #D29922; border: 1px solid rgba(210,153,34,0.2); }
.nc-chip-fail { background: rgba(248,81,73,0.1); color: #F85149; border: 1px solid rgba(248,81,73,0.2); }
.nc-card-r { font-size: 11.5px; color: #6E7681; line-height: 1.55; margin-bottom: 2px; }
.nc-card-ok { font-size: 11.5px; color: #3FB950; font-weight: 500; }
.nc-card-m {
    margin-top: 9px; padding: 8px 10px; background: #0D1117;
    border: 1px solid #30363D; border-radius: 5px;
    font-size: 10.5px; color: #8B949E;
    font-family: 'SF Mono','Fira Code',monospace; line-height: 1.8;
}
.sv-key   { color: #9CDCFE; }
.sv-str   { color: #CE9178; }
.sv-num   { color: #B5CEA8; }
.sv-kw    { color: #569CD6; }
.sv-punct { color: #6E7681; }

/* ── Footer ── */
.nc-foot {
    display: flex; align-items: center; justify-content: space-between;
    padding: 13px 0 2px; border-top: 1px solid #21262D; margin-top: 18px;
}
.nc-foot-m { font-size: 11px; color: #484F58; font-family: 'SF Mono','Fira Code',monospace; }
.nc-foot-t {
    background: #161B22; border: 1px solid #30363D; color: #484F58;
    font-size: 10px; padding: 3px 9px; border-radius: 4px;
    font-family: 'SF Mono','Fira Code',monospace;
}

/* ── Misc ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #30363D; border-radius: 3px; }
[data-testid="stVerticalBlock"] > div { gap: 0 !important; }
.stMarkdown p { color: #8B949E; }
</style>
""", unsafe_allow_html=True)

BASE = os.path.dirname(__file__)

@st.cache_resource
def load_gate():
    with open(os.path.join(BASE, "config.yaml")) as f:
        cfg = yaml.safe_load(f)
    return QualityGate(os.path.join(BASE, "sample_corpus/published"), cfg), cfg

gate, _ = load_gate()

SAMPLES = {
    "tensor-vs-pipeline-parallelism  ->  expected PASS":
        "sample_corpus/incoming/tensor-vs-pipeline-parallelism.md",
    "flash-attention-long-context-serving  ->  expected PASS":
        "sample_corpus/incoming/flash-attention-long-context-serving.md",
    "agentic-control-plane  ->  expected PASS":
        "sample_corpus/incoming/agentic-control-plane.md",
    "gb300-architecture-explained  ->  expected FLAG":
        "sample_corpus/incoming/gb300-architecture-explained.md",
    "vllm-vs-tensorrt-llm-production  ->  expected FLAG":
        "sample_corpus/incoming/vllm-vs-tensorrt-llm-production.md",
    "multi-gpu-cloud-vendor-lock-in  ->  expected FLAG":
        "sample_corpus/incoming/multi-gpu-cloud-vendor-lock-in.md",
    "h200-vs-h100-training  ->  expected FLAG":
        "sample_corpus/incoming/h200-vs-h100-training.md",
    "a100-vs-h100-llm-serving  ->  expected FAIL":
        "sample_corpus/incoming/a100-vs-h100-llm-serving.md",
    "why-gpu-cloud-india  ->  expected FAIL":
        "sample_corpus/incoming/why-gpu-cloud-india.md",
}

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="nc-header">
  <div class="nc-logo">
    <div class="nc-logo-icon">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
           stroke="#052E16" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
      </svg>
    </div>
    <div>
      <div class="nc-title">NeevCloud Content Gate</div>
      <div class="nc-sub">Automated quality circuit-breaker for content pipelines</div>
    </div>
  </div>
  <div class="nc-live"><span class="nc-dot"></span>LIVE</div>
</div>
""", unsafe_allow_html=True)

# ── Stats ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="nc-stats">
  <div class="nc-stat" style="--ac:#22C55E">
    <div class="nc-stat-v g">6</div>
    <div class="nc-stat-l">Quality Checks</div>
  </div>
  <div class="nc-stat" style="--ac:#58A6FF">
    <div class="nc-stat-v b">3</div>
    <div class="nc-stat-l">Content Classes</div>
  </div>
  <div class="nc-stat" style="--ac:#58A6FF">
    <div class="nc-stat-v b">9</div>
    <div class="nc-stat-l">Sample Posts</div>
  </div>
  <div class="nc-stat" style="--ac:#22C55E">
    <div class="nc-stat-v g">100%</div>
    <div class="nc-stat-l">Automated</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Sample selector ───────────────────────────────────────────────────────────
st.markdown('<div class="nc-lbl">Load Sample</div>', unsafe_allow_html=True)
sample_choice = st.selectbox(
    "sample", ["- paste your own -"] + list(SAMPLES.keys()),
    label_visibility="collapsed",
)

if sample_choice != "- paste your own -":
    p = parse_markdown(os.path.join(BASE, SAMPLES[sample_choice]))
    d_title, d_slug, d_kw = p.title, p.slug, p.primary_keyword
    d_cluster, d_class, d_body = p.cluster_id, p.content_class, p.body
else:
    d_title = d_slug = d_kw = d_cluster = ""
    d_class, d_body = "mid", ""

st.markdown('<hr class="nc-hr">', unsafe_allow_html=True)

# ── Inputs ────────────────────────────────────────────────────────────────────
left, right = st.columns([1, 2], gap="medium")

with left:
    st.markdown('<div class="nc-lbl">Post Metadata</div>', unsafe_allow_html=True)
    title   = st.text_input("Title",           value=d_title,   key=f"t_{sample_choice}")
    slug    = st.text_input("Slug",            value=d_slug,    key=f"s_{sample_choice}")
    keyword = st.text_input("Primary Keyword", value=d_kw,      key=f"k_{sample_choice}")
    cluster = st.text_input("Cluster ID",      value=d_cluster, key=f"c_{sample_choice}")
    _classes = ["mid", "pillar", "programmatic"]
    content_class = st.selectbox(
        "Content Class", _classes,
        index=_classes.index(d_class) if d_class in _classes else 0,
        key=f"cl_{sample_choice}",
    )

with right:
    st.markdown('<div class="nc-lbl">Post Body - Markdown</div>', unsafe_allow_html=True)
    body = st.text_area(
        "body", value=d_body, height=294,
        label_visibility="collapsed", key=f"b_{sample_choice}",
    )

st.markdown('<hr class="nc-hr">', unsafe_allow_html=True)
run = st.button("Run Quality Gate", type="primary", use_container_width=True)


def _fmt(v, depth=0):
    """Recursively render a Python value as syntax-highlighted HTML."""
    if isinstance(v, bool):
        return f'<span class="sv-kw">{str(v).lower()}</span>'
    if v is None:
        return '<span class="sv-kw">null</span>'
    if isinstance(v, (int, float)):
        return f'<span class="sv-num">{v}</span>'
    if isinstance(v, str):
        s = (v[:22] + "...") if len(v) > 25 else v
        return f'<span class="sv-str">\'{s}\'</span>'
    if isinstance(v, list):
        if not v:
            return '<span class="sv-kw">[]</span>'
        if depth >= 1:
            return f'<span class="sv-punct">[</span><span class="sv-num">{len(v)} items</span><span class="sv-punct">]</span>'
        parts = [_fmt(i, depth + 1) for i in v[:3]]
        tail = '<span class="sv-punct">, ...</span>' if len(v) > 3 else ""
        return (f'<span class="sv-punct">[</span>'
                + '<span class="sv-punct">, </span>'.join(parts) + tail
                + '<span class="sv-punct">]</span>')
    if isinstance(v, dict):
        if not v:
            return '<span class="sv-kw">{}</span>'
        pairs = []
        for dk, dv in list(v.items())[:3]:
            pairs.append(
                f'<span class="sv-key">{dk}</span>'
                f'<span class="sv-punct">: </span>{_fmt(dv, depth + 1)}'
            )
        return ('<span class="sv-punct">{{</span>'
                + '<span class="sv-punct">, </span>'.join(pairs)
                + '<span class="sv-punct">}}</span>')
    return f'<span class="sv-str">{v}</span>'


def _metrics_html(metrics):
    lines = []
    for k, v in metrics.items():
        lines.append(
            f'<span class="sv-key">{k}</span>'
            f'<span class="sv-punct">: </span>{_fmt(v)}'
        )
    return "<br>".join(lines)

# ── Results ───────────────────────────────────────────────────────────────────
if run:
    if not body.strip():
        st.warning("Paste some content first.")
        st.stop()

    post = Post(
        slug=slug or "untitled",
        title=title or slug or "untitled",
        primary_keyword=keyword,
        cluster_id=cluster,
        content_class=content_class,
        body=body,
        path="<live-input>",
    )

    report = gate.evaluate(post)
    v = report.verdict

    pass_count = sum(1 for c in report.checks if c.status == "PASS")
    total = len(report.checks)

    ICON = {"PASS": "&#10003;", "FLAG": "&#9873;", "FAIL": "&#10007;"}
    DESC = {
        "PASS": "All checks cleared - queued for publish",
        "FLAG": "Flagged for human review before publishing",
        "FAIL": "Blocked - must return to content generation",
    }
    CSS_V = {"PASS": "nc-v-pass", "FLAG": "nc-v-flag", "FAIL": "nc-v-fail"}
    CSS_S = {"PASS": "pass", "FLAG": "flag", "FAIL": "fail"}

    # Verdict
    st.markdown(f"""
<div class="nc-v {CSS_V[v]}">
  <div class="nc-v-ico">{ICON[v]}</div>
  <div class="nc-v-body">
    <div class="nc-v-status">{v}</div>
    <div class="nc-v-desc">{DESC[v]}</div>
  </div>
  <div class="nc-v-score">
    <div class="nc-v-score-n">{pass_count}/{total}</div>
    <div class="nc-v-score-l">checks passed</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # Check cards
    st.markdown('<div class="nc-lbl">Check Results</div>', unsafe_allow_html=True)

    cards = []
    for check in report.checks:
        s = CSS_S[check.status]
        name = check.name.replace("_", " ").replace("-", " ").title()
        reasons = "".join(
            f'<div class="nc-card-r">&#8250; {r}</div>' for r in check.reasons
        ) if check.reasons else '<div class="nc-card-ok">&#10003; All clear</div>'
        metrics = ""
        if check.metrics:
            metrics = f'<div class="nc-card-m">{_metrics_html(check.metrics)}</div>'
        cards.append(f"""
<div class="nc-card nc-card-{s}">
  <div class="nc-card-h">
    <div class="nc-card-n">{name}</div>
    <div class="nc-chip nc-chip-{s}">{check.status}</div>
  </div>
  {reasons}{metrics}
</div>""")

    st.markdown(f'<div class="nc-grid">{"".join(cards)}</div>', unsafe_allow_html=True)

    # Footer
    st.markdown(f"""
<div class="nc-foot">
  <div class="nc-foot-m">
    {post.word_count} words &nbsp;·&nbsp;
    cluster: {post.cluster_id or "-"} &nbsp;·&nbsp;
    class: {post.content_class}
  </div>
  <div class="nc-foot-t">neevcloud/content-gate v1.0</div>
</div>
""", unsafe_allow_html=True)
