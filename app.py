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

# ── Theme state ───────────────────────────────────────────────────────────────
if "dark" not in st.session_state:
    st.session_state.dark = True

DARK = st.session_state.dark

# ── Design tokens (GitHub light / dark) ──────────────────────────────────────
if DARK:
    T = dict(
        base       = "#0D1117",
        surface    = "#161B22",
        surface2   = "#21262D",
        border     = "#30363D",
        border_hi  = "#484F58",
        text1      = "#E6EDF3",
        text2      = "#8B949E",
        muted      = "#6E7681",
        accent     = "#3FB950",
        accent_bg  = "#0A1F0F",
        accent_bdr = "rgba(63,185,80,0.3)",
        amber      = "#D29922",
        amber_bg   = "#1A1300",
        amber_bdr  = "rgba(210,153,34,0.35)",
        red        = "#F85149",
        red_bg     = "#1A0606",
        red_bdr    = "rgba(248,81,73,0.35)",
        btn_txt    = "#052E16",
        meta_bg    = "#0D1117",
        sv_key     = "#9CDCFE",
        sv_str     = "#CE9178",
        sv_num     = "#B5CEA8",
        sv_kw      = "#569CD6",
        sv_punct   = "#6E7681",
    )
else:
    T = dict(
        base       = "#FFFFFF",
        surface    = "#F6F8FA",
        surface2   = "#EAEEF2",
        border     = "#D0D7DE",
        border_hi  = "#8C959F",
        text1      = "#1F2328",
        text2      = "#636C76",
        muted      = "#6E7781",
        accent     = "#1A7F37",
        accent_bg  = "#DAFBE1",
        accent_bdr = "rgba(26,127,55,0.3)",
        amber      = "#9A6700",
        amber_bg   = "#FFF8C5",
        amber_bdr  = "rgba(154,103,0,0.3)",
        red        = "#CF222E",
        red_bg     = "#FFEBE9",
        red_bdr    = "rgba(207,34,46,0.3)",
        btn_txt    = "#FFFFFF",
        meta_bg    = "#F6F8FA",
        sv_key     = "#0550AE",
        sv_str     = "#0A3069",
        sv_num     = "#1A7F37",
        sv_kw      = "#8250DF",
        sv_punct   = "#8C959F",
    )

css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, .stApp {{ font-family: 'Inter', sans-serif !important; }}
.stApp {{ background: {T['base']} !important; }}
#MainMenu, footer, header, [data-testid="stDecoration"],
[data-testid="stStatusWidget"], [data-testid="stHeader"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {{ display: none !important; }}
.block-container {{ padding-top: 1.2rem !important; max-width: 1160px !important; }}

/* ── Inputs ── */
input, input[type="text"] {{
    background: {T['surface']} !important;
    border: 1px solid {T['border_hi']} !important;
    border-radius: 6px !important;
    color: {T['text1']} !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
}}
input:focus, input[type="text"]:focus {{
    border-color: {T['accent']} !important;
    box-shadow: 0 0 0 3px {T['accent_bg']} !important;
    outline: none !important;
}}
textarea {{
    background: {T['surface']} !important;
    border: 1px solid {T['border_hi']} !important;
    border-radius: 6px !important;
    color: {T['text1']} !important;
    font-family: Menlo, Monaco, 'SF Mono', 'Fira Code', monospace !important;
    font-size: 12px !important;
    line-height: 1.65 !important;
}}
textarea:focus {{
    border-color: {T['accent']} !important;
    box-shadow: 0 0 0 3px {T['accent_bg']} !important;
    outline: none !important;
}}
.stTextInput label, .stTextArea label, .stSelectbox label {{
    color: {T['muted']} !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
}}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {{
    background: {T['surface']} !important;
    border: 1px solid {T['border_hi']} !important;
    border-radius: 6px !important;
    color: {T['text1']} !important;
}}
[data-testid="stSelectbox"] svg {{ fill: {T['muted']} !important; }}

/* ── All buttons default: ghost/minimal ── */
.stButton > button {{
    background: {T['surface']} !important;
    border: 1px solid {T['border']} !important;
    color: {T['text2']} !important;
    font-size: 12px !important; font-weight: 500 !important;
    padding: 6px 14px !important; border-radius: 6px !important;
    box-shadow: none !important; cursor: pointer !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color 0.15s, color 0.15s !important;
}}
.stButton > button:hover {{
    border-color: {T['border_hi']} !important;
    color: {T['text1']} !important;
    transform: none !important; box-shadow: none !important;
}}
/* ── Run Gate button: override primary only ── */
[data-testid="baseButton-primary"],
button[kind="primary"] {{
    background: linear-gradient(135deg, {T['accent']} 0%, {'#16A34A' if DARK else '#116329'} 100%) !important;
    color: {T['btn_txt']} !important;
    font-weight: 700 !important; font-size: 14px !important;
    letter-spacing: 0.2px !important; border: none !important;
    border-radius: 7px !important; padding: 13px 28px !important;
    box-shadow: 0 0 0 1px {T['accent_bdr']}, 0 4px 20px {T['accent_bg']} !important;
    transition: box-shadow 0.2s, transform 0.15s !important;
}}
[data-testid="baseButton-primary"]:hover,
button[kind="primary"]:hover {{
    box-shadow: 0 0 0 1px {T['accent']}, 0 6px 28px {T['accent_bg']} !important;
    transform: translateY(-1px) !important;
}}

/* ── Divider ── */
.nc-hr {{ border: none; border-top: 1px solid {T['surface2']}; margin: 6px 0; }}

/* ── Header ── */
.nc-header {{
    display: flex; align-items: center; gap: 16px;
    padding: 16px 0 20px; border-bottom: 1px solid {T['surface2']}; margin-bottom: 22px;
}}
.nc-logo {{ display: flex; align-items: center; gap: 13px; }}
.nc-logo-icon {{
    width: 38px; height: 38px; border-radius: 9px; flex-shrink: 0;
    background: linear-gradient(135deg, {T['accent']} 0%, {'#15803D' if DARK else '#116329'} 100%);
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 0 20px {T['accent_bg']};
}}
.nc-title {{ font-size: 17px; font-weight: 700; color: {T['text1']}; letter-spacing: -0.3px; }}
.nc-sub {{ font-size: 13px; color: {T['muted']}; margin-top: 3px; }}
/* right-align toggle col - scope to header row only */
[data-testid="stHorizontalBlock"]:first-child [data-testid="column"]:last-child {{
    display: flex !important; justify-content: flex-end !important;
    align-items: flex-start !important; padding-top: 14px !important;
}}
.nc-live {{
    display: flex; align-items: center; gap: 7px;
    background: {T['accent_bg']}; border: 1px solid {T['accent_bdr']};
    color: {T['accent']}; font-size: 11px; font-weight: 600;
    padding: 5px 12px; border-radius: 20px; letter-spacing: 0.4px;
}}
.nc-dot {{
    width: 7px; height: 7px; background: {T['accent']}; border-radius: 50%;
    {'box-shadow: 0 0 7px ' + T['accent'] + ';' if DARK else ''} display: inline-block;
}}

/* ── Stats ── */
.nc-stats {{
    display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin-bottom: 24px;
}}
.nc-stat {{
    background: {T['surface']}; border: 1px solid {T['border']}; border-radius: 9px;
    padding: 15px 18px; position: relative; overflow: hidden;
}}
.nc-stat::before {{
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: var(--ac, {T['border']});
}}
.nc-stat-v {{ font-size: 26px; font-weight: 800; letter-spacing: -1px; line-height: 1; }}
.nc-stat-l {{ font-size: 10px; color: {T['muted']}; font-weight: 600; margin-top: 5px;
             text-transform: uppercase; letter-spacing: 0.9px; }}
.g {{ color: {T['accent']}; }} .b {{ color: {'#58A6FF' if DARK else '#0969DA'}; }}

/* ── Section label ── */
.nc-lbl {{
    font-size: 10px; font-weight: 700; color: {T['muted']}; text-transform: uppercase;
    letter-spacing: 1.1px; margin-bottom: 9px; display: flex; align-items: center; gap: 8px;
}}
.nc-lbl::after {{ content: ''; flex: 1; height: 1px; background: {T['surface2']}; }}

/* ── Verdict ── */
.nc-v {{ border-radius: 10px; padding: 20px 24px; margin: 6px 0 20px;
         display: flex; align-items: center; gap: 18px; }}
.nc-v-pass {{ background: {T['accent_bg']}; border: 1px solid {T['accent_bdr']};
              box-shadow: 0 0 32px {T['accent_bg']}; }}
.nc-v-flag {{ background: {T['amber_bg']}; border: 1px solid {T['amber_bdr']}; }}
.nc-v-fail {{ background: {T['red_bg']}; border: 1px solid {T['red_bdr']}; }}
.nc-v-ico {{
    width: 52px; height: 52px; border-radius: 10px; display: flex;
    align-items: center; justify-content: center; font-size: 24px;
    font-weight: 800; flex-shrink: 0;
}}
.nc-v-pass .nc-v-ico {{ background: {T['accent_bg']}; color: {T['accent']}; }}
.nc-v-flag .nc-v-ico {{ background: {T['amber_bg']}; color: {T['amber']}; }}
.nc-v-fail .nc-v-ico {{ background: {T['red_bg']}; color: {T['red']}; }}
.nc-v-body {{ flex: 1; }}
.nc-v-status {{ font-size: 24px; font-weight: 800; letter-spacing: -0.6px; line-height: 1; }}
.nc-v-pass .nc-v-status {{ color: {T['accent']}; }}
.nc-v-flag .nc-v-status {{ color: {T['amber']}; }}
.nc-v-fail .nc-v-status {{ color: {T['red']}; }}
.nc-v-desc {{ font-size: 13px; margin-top: 4px; color: {T['muted']}; }}
.nc-v-score {{ text-align: right; flex-shrink: 0; }}
.nc-v-score-n {{ font-size: 32px; font-weight: 800; letter-spacing: -1px;
                line-height: 1; color: {T['border_hi']}; }}
.nc-v-score-l {{ font-size: 10px; color: {T['muted']}; text-transform: uppercase;
                letter-spacing: 0.9px; margin-top: 3px; font-weight: 600; }}

/* ── Check grid ── */
.nc-grid {{ display: grid; grid-template-columns: repeat(3,1fr); gap: 11px; margin-top: 4px; }}
.nc-card {{
    background: {T['surface']}; border: 1px solid {T['border']}; border-radius: 9px; padding: 14px 15px;
}}
.nc-card-pass {{ border-color: {T['accent_bdr']}; }}
.nc-card-flag {{ border-color: {T['amber_bdr']}; }}
.nc-card-fail {{ border-color: {T['red_bdr']}; }}
.nc-card-h {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 9px; }}
.nc-card-n {{ font-size: 12px; font-weight: 600; color: {T['text2']}; }}
.nc-chip {{ font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 4px; letter-spacing: 0.7px; }}
.nc-chip-pass {{ background: {T['accent_bg']}; color: {T['accent']}; border: 1px solid {T['accent_bdr']}; }}
.nc-chip-flag {{ background: {T['amber_bg']}; color: {T['amber']}; border: 1px solid {T['amber_bdr']}; }}
.nc-chip-fail {{ background: {T['red_bg']}; color: {T['red']}; border: 1px solid {T['red_bdr']}; }}
.nc-card-r {{ font-size: 11.5px; color: {T['muted']}; line-height: 1.55; margin-bottom: 2px; }}
.nc-card-ok {{ font-size: 11.5px; color: {T['accent']}; font-weight: 500; }}
.nc-card-m {{
    margin-top: 9px; padding: 8px 10px; background: {T['meta_bg']};
    border: 1px solid {T['surface2']}; border-radius: 5px;
    font-size: 10.5px; color: {T['text2']};
    font-family: Menlo, Monaco, 'SF Mono', 'Fira Code', monospace; line-height: 1.8;
}}
.sv-key   {{ color: {T['sv_key']}; }}
.sv-str   {{ color: {T['sv_str']}; }}
.sv-num   {{ color: {T['sv_num']}; }}
.sv-kw    {{ color: {T['sv_kw']}; }}
.sv-punct {{ color: {T['sv_punct']}; }}

/* ── Footer ── */
.nc-foot {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 13px 0 2px; border-top: 1px solid {T['surface2']}; margin-top: 18px;
}}
.nc-foot-m {{
    font-size: 11px; color: {T['muted']};
    font-family: Menlo, Monaco, 'SF Mono', 'Fira Code', monospace;
}}
.nc-foot-t {{
    background: {T['accent_bg']}; border: 1px solid {T['accent_bdr']}; color: {T['accent']};
    font-size: 10px; font-weight: 500; padding: 3px 10px; border-radius: 4px;
    font-family: Menlo, Monaco, 'SF Mono', 'Fira Code', monospace; letter-spacing: 0.3px;
}}

/* ── Misc ── */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {T['border']}; border-radius: 3px; }}
[data-testid="stVerticalBlock"] > div {{ gap: 0 !important; }}
.stMarkdown p {{ color: {T['text2']}; }}

/* ── Responsive ── */
@media (max-width: 640px) {{
    .nc-stats {{ grid-template-columns: repeat(2,1fr) !important; }}
    .nc-grid  {{ grid-template-columns: 1fr !important; }}
    .nc-v     {{ flex-direction: column; gap: 10px; }}
    .nc-v-score {{ text-align: left; }}
}}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

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
h_left, h_right = st.columns([9, 1])
with h_left:
    st.markdown(f"""
<div class="nc-header">
  <div class="nc-logo">
    <div class="nc-logo-icon">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
           stroke="{'#052E16' if DARK else '#FFFFFF'}" stroke-width="2.5"
           stroke-linecap="round" stroke-linejoin="round">
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

with h_right:
    if st.button("☀" if DARK else "◑"):
        st.session_state.dark = not DARK
        st.rerun()

# ── Stats ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="nc-stats">
  <div class="nc-stat" style="--ac:{T['accent']}">
    <div class="nc-stat-v g">6</div>
    <div class="nc-stat-l">Quality Checks</div>
  </div>
  <div class="nc-stat" style="--ac:{'#58A6FF' if DARK else '#0969DA'}">
    <div class="nc-stat-v b">3</div>
    <div class="nc-stat-l">Content Classes</div>
  </div>
  <div class="nc-stat" style="--ac:{'#58A6FF' if DARK else '#0969DA'}">
    <div class="nc-stat-v b">9</div>
    <div class="nc-stat-l">Sample Posts</div>
  </div>
  <div class="nc-stat" style="--ac:{T['accent']}">
    <div class="nc-stat-v g">100%</div>
    <div class="nc-stat-l">Automated</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Sample selector ───────────────────────────────────────────────────────────
st.markdown('<div class="nc-lbl">Load Sample</div>', unsafe_allow_html=True)
sample_choice = st.selectbox(
    "sample", ["paste your own"] + list(SAMPLES.keys()),
    label_visibility="collapsed",
)

if sample_choice != "paste your own":
    p = parse_markdown(os.path.join(BASE, SAMPLES[sample_choice]))
    d_title, d_slug, d_kw = p.title, p.slug, p.primary_keyword
    d_cluster, d_class, d_body = p.cluster_id, p.content_class, p.body
else:
    d_title = d_slug = d_kw = d_cluster = ""
    d_class, d_body = "mid", ""

st.markdown('<hr class="nc-hr">', unsafe_allow_html=True)

# ── Inputs ────────────────────────────────────────────────────────────────────
left, right = st.columns([1, 2], gap="small")

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
    # Height matches left column (5 inputs x ~58px + label = ~310px)
    body = st.text_area(
        "body", value=d_body, height=305,
        label_visibility="collapsed", key=f"b_{sample_choice}",
    )

st.markdown('<hr class="nc-hr">', unsafe_allow_html=True)
run = st.button("Run Quality Gate", type="primary", use_container_width=True)


# ── Syntax formatter ──────────────────────────────────────────────────────────
def _fmt(v, depth=0):
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
            return (f'<span class="sv-punct">[</span>'
                    f'<span class="sv-num">{len(v)} items</span>'
                    f'<span class="sv-punct">]</span>')
        parts = [_fmt(i, depth + 1) for i in v[:3]]
        tail = '<span class="sv-punct">, ...</span>' if len(v) > 3 else ""
        return (f'<span class="sv-punct">[</span>'
                + '<span class="sv-punct">, </span>'.join(parts) + tail
                + '<span class="sv-punct">]</span>')
    if isinstance(v, dict):
        if not v:
            return '<span class="sv-kw">{{}}</span>'
        pairs = [
            f'<span class="sv-key">{dk}</span>'
            f'<span class="sv-punct">: </span>{_fmt(dv, depth + 1)}'
            for dk, dv in list(v.items())[:3]
        ]
        return ('<span class="sv-punct">{{</span>'
                + '<span class="sv-punct">, </span>'.join(pairs)
                + '<span class="sv-punct">}}</span>')
    return f'<span class="sv-str">{v}</span>'


def _metrics_html(metrics):
    return "<br>".join(
        f'<span class="sv-key">{k}</span>'
        f'<span class="sv-punct">: </span>{_fmt(v)}'
        for k, v in metrics.items()
    )


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

    ICON  = {"PASS": "&#10003;", "FLAG": "&#9873;", "FAIL": "&#10007;"}
    DESC  = {
        "PASS": "All checks cleared - queued for publish",
        "FLAG": "Flagged for human review before publishing",
        "FAIL": "Blocked - must return to content generation",
    }
    CSS_V = {"PASS": "nc-v-pass", "FLAG": "nc-v-flag", "FAIL": "nc-v-fail"}
    CSS_S = {"PASS": "pass",      "FLAG": "flag",       "FAIL": "fail"}

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

    st.markdown('<div class="nc-lbl">Check Results</div>', unsafe_allow_html=True)

    cards = []
    for check in report.checks:
        s = CSS_S[check.status]
        name = check.name.replace("_", " ").replace("-", " ").title()
        reasons = "".join(
            f'<div class="nc-card-r">&#8250; {r}</div>' for r in check.reasons
        ) if check.reasons else '<div class="nc-card-ok">&#10003; All clear</div>'
        metrics = (f'<div class="nc-card-m">{_metrics_html(check.metrics)}</div>'
                   if check.metrics else "")
        cards.append(f"""
<div class="nc-card nc-card-{s}">
  <div class="nc-card-h">
    <div class="nc-card-n">{name}</div>
    <div class="nc-chip nc-chip-{s}">{check.status}</div>
  </div>
  {reasons}{metrics}
</div>""")

    st.markdown(f'<div class="nc-grid">{"".join(cards)}</div>', unsafe_allow_html=True)

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
