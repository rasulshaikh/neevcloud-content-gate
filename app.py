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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Base ── */
.stApp, .stApp * { font-family: 'Inter', sans-serif !important; }
.stApp { background: #030712 !important; }
#MainMenu, footer { visibility: hidden; }
.stDeployButton { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

/* ── Header ── */
.nc-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 0 22px 0;
    border-bottom: 1px solid #0F172A;
    margin-bottom: 24px;
}
.nc-logo {
    display: flex;
    align-items: center;
    gap: 14px;
}
.nc-logo-icon {
    width: 40px;
    height: 40px;
    background: linear-gradient(135deg, #22C55E 0%, #15803D 100%);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 24px rgba(34, 197, 94, 0.35);
    flex-shrink: 0;
}
.nc-logo-icon svg { display: block; }
.nc-title {
    font-size: 18px;
    font-weight: 700;
    color: #F1F5F9;
    letter-spacing: -0.4px;
    line-height: 1.2;
}
.nc-subtitle {
    font-size: 12px;
    color: #475569;
    font-weight: 400;
    margin-top: 3px;
    letter-spacing: 0.1px;
}
.nc-live-badge {
    background: #0A1F0F;
    border: 1px solid rgba(34, 197, 94, 0.4);
    color: #4ADE80;
    font-size: 11px;
    font-weight: 600;
    padding: 5px 12px;
    border-radius: 20px;
    letter-spacing: 0.5px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.nc-live-dot {
    width: 7px;
    height: 7px;
    background: #22C55E;
    border-radius: 50%;
    box-shadow: 0 0 8px #22C55E;
    display: inline-block;
}

/* ── Stats Row ── */
.nc-stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 28px;
}
.nc-stat {
    background: #0A0F1A;
    border: 1px solid #0F172A;
    border-radius: 10px;
    padding: 16px 20px;
    position: relative;
    overflow: hidden;
}
.nc-stat::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent-color, #1E293B);
    opacity: 0.6;
}
.nc-stat-pass::before { --accent-color: #22C55E; }
.nc-stat-flag::before { --accent-color: #F59E0B; }
.nc-stat-fail::before { --accent-color: #EF4444; }
.nc-stat-neutral::before { --accent-color: #3B82F6; }
.nc-stat-value {
    font-size: 28px;
    font-weight: 800;
    color: #F1F5F9;
    line-height: 1;
    letter-spacing: -1px;
}
.nc-stat-value-pass { color: #22C55E; }
.nc-stat-value-flag { color: #F59E0B; }
.nc-stat-value-fail { color: #EF4444; }
.nc-stat-value-neutral { color: #60A5FA; }
.nc-stat-label {
    font-size: 11px;
    color: #475569;
    font-weight: 500;
    margin-top: 5px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

/* ── Section Labels ── */
.nc-label {
    font-size: 10px;
    font-weight: 600;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.nc-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #0F172A;
}

/* ── Input overrides ── */
.stTextInput > label,
.stTextArea > label,
.stSelectbox > label {
    color: #475569 !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
    margin-bottom: 4px !important;
}
.stTextInput > div > div > input {
    background: #0A0F1A !important;
    border: 1px solid #0F172A !important;
    border-radius: 8px !important;
    color: #CBD5E1 !important;
    font-size: 13px !important;
    padding: 8px 12px !important;
    transition: border-color 0.15s ease !important;
}
.stTextInput > div > div > input:focus {
    border-color: #22C55E !important;
    box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.1) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder { color: #334155 !important; }

.stTextArea > div > div > textarea {
    background: #0A0F1A !important;
    border: 1px solid #0F172A !important;
    border-radius: 8px !important;
    color: #94A3B8 !important;
    font-size: 12px !important;
    font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', monospace !important;
    line-height: 1.6 !important;
    transition: border-color 0.15s ease !important;
}
.stTextArea > div > div > textarea:focus {
    border-color: #22C55E !important;
    box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.1) !important;
}

.stSelectbox > div > div {
    background: #0A0F1A !important;
    border: 1px solid #0F172A !important;
    border-radius: 8px !important;
    color: #CBD5E1 !important;
    font-size: 13px !important;
}
.stSelectbox > div > div:hover {
    border-color: #1E293B !important;
}
.stSelectbox [data-baseweb="select"] > div {
    background: #0A0F1A !important;
    border-color: #0F172A !important;
}
.stSelectbox svg { fill: #475569 !important; }

/* ── Run Button ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #22C55E 0%, #16A34A 100%) !important;
    color: #052E16 !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    letter-spacing: 0.2px !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 14px 28px !important;
    box-shadow: 0 4px 24px rgba(34, 197, 94, 0.3) !important;
    transition: box-shadow 0.2s ease, transform 0.15s ease !important;
    cursor: pointer !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 32px rgba(34, 197, 94, 0.5) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"]:active {
    transform: translateY(0) !important;
    box-shadow: 0 2px 12px rgba(34, 197, 94, 0.3) !important;
}

/* ── Divider ── */
.nc-hr {
    border: none;
    border-top: 1px solid #0F172A;
    margin: 22px 0;
}

/* ── Verdict Banner ── */
.nc-verdict {
    border-radius: 12px;
    padding: 22px 28px;
    margin: 8px 0 24px 0;
    display: flex;
    align-items: center;
    gap: 22px;
    position: relative;
    overflow: hidden;
}
.nc-verdict::after {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 200px;
    height: 100%;
    opacity: 0.04;
    pointer-events: none;
}
.nc-verdict-pass {
    background: linear-gradient(135deg, #071A0D 0%, #0A2010 100%);
    border: 1px solid rgba(34, 197, 94, 0.35);
    box-shadow: 0 0 0 1px rgba(34, 197, 94, 0.05), 0 8px 40px rgba(34, 197, 94, 0.08);
}
.nc-verdict-flag {
    background: linear-gradient(135deg, #150F00 0%, #1C1500 100%);
    border: 1px solid rgba(245, 158, 11, 0.35);
    box-shadow: 0 0 0 1px rgba(245, 158, 11, 0.05), 0 8px 40px rgba(245, 158, 11, 0.08);
}
.nc-verdict-fail {
    background: linear-gradient(135deg, #150505 0%, #1C0A0A 100%);
    border: 1px solid rgba(239, 68, 68, 0.35);
    box-shadow: 0 0 0 1px rgba(239, 68, 68, 0.05), 0 8px 40px rgba(239, 68, 68, 0.08);
}
.nc-verdict-icon-wrap {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    font-size: 26px;
    font-weight: 800;
    line-height: 1;
}
.nc-verdict-pass .nc-verdict-icon-wrap {
    background: rgba(34, 197, 94, 0.12);
    color: #22C55E;
    box-shadow: 0 0 20px rgba(34, 197, 94, 0.2);
}
.nc-verdict-flag .nc-verdict-icon-wrap {
    background: rgba(245, 158, 11, 0.12);
    color: #F59E0B;
    box-shadow: 0 0 20px rgba(245, 158, 11, 0.2);
}
.nc-verdict-fail .nc-verdict-icon-wrap {
    background: rgba(239, 68, 68, 0.12);
    color: #EF4444;
    box-shadow: 0 0 20px rgba(239, 68, 68, 0.2);
}
.nc-verdict-body { flex: 1; }
.nc-verdict-status {
    font-size: 26px;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -0.8px;
}
.nc-verdict-pass .nc-verdict-status { color: #4ADE80; }
.nc-verdict-flag .nc-verdict-status { color: #FCD34D; }
.nc-verdict-fail .nc-verdict-status { color: #F87171; }
.nc-verdict-desc {
    font-size: 13px;
    font-weight: 400;
    margin-top: 5px;
    line-height: 1.4;
}
.nc-verdict-pass .nc-verdict-desc { color: #4ADE8099; }
.nc-verdict-flag .nc-verdict-desc { color: #FCD34D99; }
.nc-verdict-fail .nc-verdict-desc { color: #F8717199; }
.nc-verdict-score {
    text-align: right;
    flex-shrink: 0;
}
.nc-verdict-score-num {
    font-size: 36px;
    font-weight: 800;
    letter-spacing: -1.5px;
    line-height: 1;
    opacity: 0.25;
    color: #F1F5F9;
}
.nc-verdict-score-label {
    font-size: 10px;
    color: #334155;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
    font-weight: 600;
}

/* ── Check Grid ── */
.nc-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-top: 4px;
}
.nc-card {
    background: #0A0F1A;
    border: 1px solid #0F172A;
    border-radius: 10px;
    padding: 15px 16px;
    transition: border-color 0.2s ease;
}
.nc-card-pass { border-color: rgba(34, 197, 94, 0.15); }
.nc-card-flag { border-color: rgba(245, 158, 11, 0.2); }
.nc-card-fail { border-color: rgba(239, 68, 68, 0.2); }
.nc-card-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
}
.nc-card-name {
    font-size: 12px;
    font-weight: 600;
    color: #94A3B8;
    text-transform: capitalize;
    letter-spacing: 0.1px;
}
.nc-chip {
    font-size: 10px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 4px;
    letter-spacing: 0.8px;
}
.nc-chip-pass {
    background: rgba(34, 197, 94, 0.1);
    color: #4ADE80;
    border: 1px solid rgba(34, 197, 94, 0.2);
}
.nc-chip-flag {
    background: rgba(245, 158, 11, 0.1);
    color: #FCD34D;
    border: 1px solid rgba(245, 158, 11, 0.2);
}
.nc-chip-fail {
    background: rgba(239, 68, 68, 0.1);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.2);
}
.nc-card-reason {
    font-size: 11.5px;
    color: #64748B;
    line-height: 1.55;
    margin-bottom: 2px;
}
.nc-card-ok {
    font-size: 11.5px;
    color: #22863A;
    font-weight: 500;
}
.nc-card-metrics {
    margin-top: 10px;
    padding: 8px 10px;
    background: #060A10;
    border-radius: 6px;
    border: 1px solid #0A0F1A;
    font-size: 10.5px;
    color: #334155;
    font-family: 'SF Mono', 'Fira Code', monospace !important;
    line-height: 1.7;
}

/* ── Footer ── */
.nc-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 0 4px 0;
    border-top: 1px solid #0F172A;
    margin-top: 20px;
}
.nc-meta {
    font-size: 11px;
    color: #334155;
    font-family: 'SF Mono', 'Fira Code', monospace;
    letter-spacing: 0.2px;
}
.nc-tag {
    background: #0A0F1A;
    border: 1px solid #0F172A;
    color: #334155;
    font-size: 10px;
    font-weight: 500;
    padding: 3px 9px;
    border-radius: 4px;
    font-family: 'SF Mono', 'Fira Code', monospace;
}

/* ── Streamlit block/column spacing ── */
[data-testid="stVerticalBlock"] > div { gap: 0 !important; }
.stMarkdown { margin-bottom: 0 !important; }
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1200px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #1E293B; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #334155; }

/* ── Warning ── */
.stAlert { background: #0A0F1A !important; border-color: #1E293B !important; }
</style>
""", unsafe_allow_html=True)

BASE = os.path.dirname(__file__)

@st.cache_resource
def load_gate():
    with open(os.path.join(BASE, "config.yaml")) as f:
        config = yaml.safe_load(f)
    gate = QualityGate(os.path.join(BASE, "sample_corpus/published"), config)
    return gate, config

gate, _ = load_gate()

SAMPLES = {
    "tensor-vs-pipeline-parallelism  ->  expected PASS": "sample_corpus/incoming/tensor-vs-pipeline-parallelism.md",
    "flash-attention-long-context-serving  ->  expected PASS": "sample_corpus/incoming/flash-attention-long-context-serving.md",
    "agentic-control-plane  ->  expected PASS": "sample_corpus/incoming/agentic-control-plane.md",
    "gb300-architecture-explained  ->  expected FLAG": "sample_corpus/incoming/gb300-architecture-explained.md",
    "vllm-vs-tensorrt-llm-production  ->  expected FLAG": "sample_corpus/incoming/vllm-vs-tensorrt-llm-production.md",
    "multi-gpu-cloud-vendor-lock-in  ->  expected FLAG": "sample_corpus/incoming/multi-gpu-cloud-vendor-lock-in.md",
    "h200-vs-h100-training  ->  expected FLAG": "sample_corpus/incoming/h200-vs-h100-training.md",
    "a100-vs-h100-llm-serving  ->  expected FAIL": "sample_corpus/incoming/a100-vs-h100-llm-serving.md",
    "why-gpu-cloud-india  ->  expected FAIL": "sample_corpus/incoming/why-gpu-cloud-india.md",
}

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="nc-header">
  <div class="nc-logo">
    <div class="nc-logo-icon">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#052E16" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
      </svg>
    </div>
    <div>
      <div class="nc-title">NeevCloud Content Gate</div>
      <div class="nc-subtitle">Automated quality circuit-breaker for content pipelines</div>
    </div>
  </div>
  <div class="nc-live-badge">
    <span class="nc-live-dot"></span>
    LIVE
  </div>
</div>
""", unsafe_allow_html=True)

# ── Stats Bar ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="nc-stats">
  <div class="nc-stat nc-stat-pass">
    <div class="nc-stat-value nc-stat-value-pass">6</div>
    <div class="nc-stat-label">Quality Checks</div>
  </div>
  <div class="nc-stat nc-stat-neutral">
    <div class="nc-stat-value nc-stat-value-neutral">3</div>
    <div class="nc-stat-label">Content Classes</div>
  </div>
  <div class="nc-stat nc-stat-neutral">
    <div class="nc-stat-value nc-stat-value-neutral">9</div>
    <div class="nc-stat-label">Sample Posts</div>
  </div>
  <div class="nc-stat nc-stat-pass">
    <div class="nc-stat-value nc-stat-value-pass">100%</div>
    <div class="nc-stat-label">Automated</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Sample selector ───────────────────────────────────────────────────────────
st.markdown('<div class="nc-label">Load Sample</div>', unsafe_allow_html=True)

sample_choice = st.selectbox(
    "sample",
    ["- paste your own -"] + list(SAMPLES.keys()),
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
    st.markdown('<div class="nc-label">Post Metadata</div>', unsafe_allow_html=True)
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
    st.markdown('<div class="nc-label">Post Body - Markdown</div>', unsafe_allow_html=True)
    body = st.text_area(
        "body", value=d_body, height=290,
        label_visibility="collapsed", key=f"b_{sample_choice}",
    )

st.markdown('<hr class="nc-hr">', unsafe_allow_html=True)

run = st.button("Run Quality Gate", type="primary", use_container_width=True)

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
    total      = len(report.checks)

    ICON = {"PASS": "✓", "FLAG": "⚑", "FAIL": "✕"}
    DESC = {
        "PASS": "All checks cleared - post is queued for publish",
        "FLAG": "Flagged for human review before publishing",
        "FAIL": "Blocked - must return to content generation",
    }
    CSS_V = {"PASS": "nc-verdict-pass", "FLAG": "nc-verdict-flag", "FAIL": "nc-verdict-fail"}
    CSS_S = {"PASS": "pass", "FLAG": "flag", "FAIL": "fail"}

    # Verdict banner
    st.markdown(f"""
<div class="nc-verdict {CSS_V[v]}">
  <div class="nc-verdict-icon-wrap">{ICON[v]}</div>
  <div class="nc-verdict-body">
    <div class="nc-verdict-status">{v}</div>
    <div class="nc-verdict-desc">{DESC[v]}</div>
  </div>
  <div class="nc-verdict-score">
    <div class="nc-verdict-score-num">{pass_count}/{total}</div>
    <div class="nc-verdict-score-label">checks passed</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # Check result cards
    st.markdown('<div class="nc-label">Check Results</div>', unsafe_allow_html=True)

    cards = []
    for check in report.checks:
        s = CSS_S[check.status]
        name_display = check.name.replace("_", " ").replace("-", " ").title()

        if check.reasons:
            reasons_html = "".join(
                f'<div class="nc-card-reason">&#8250; {r}</div>' for r in check.reasons
            )
        else:
            reasons_html = '<div class="nc-card-ok">&#10003; All clear</div>'

        metrics_html = ""
        if check.metrics:
            lines = "<br>".join(f"{k}: {val}" for k, val in check.metrics.items())
            metrics_html = f'<div class="nc-card-metrics">{lines}</div>'

        cards.append(f"""
<div class="nc-card nc-card-{s}">
  <div class="nc-card-head">
    <div class="nc-card-name">{name_display}</div>
    <div class="nc-chip nc-chip-{s}">{check.status}</div>
  </div>
  {reasons_html}
  {metrics_html}
</div>""")

    st.markdown(f'<div class="nc-grid">{"".join(cards)}</div>', unsafe_allow_html=True)

    # Footer metadata
    st.markdown(f"""
<div class="nc-footer">
  <div class="nc-meta">
    {post.word_count} words &nbsp;·&nbsp;
    cluster: {post.cluster_id or "-"} &nbsp;·&nbsp;
    class: {post.content_class}
  </div>
  <div class="nc-tag">neevcloud/content-gate v1.0</div>
</div>
""", unsafe_allow_html=True)
