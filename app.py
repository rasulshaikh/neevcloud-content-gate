import os
import yaml
import streamlit as st
from gate.gate import QualityGate
from gate.corpus import Post, parse_markdown

st.set_page_config(
    page_title="NeevCloud Content Gate",
    page_icon="🛡️",
    layout="wide",
)

st.markdown("""
<style>
.verdict-pass{background:#0d1f13;border:1.5px solid #3fb950;border-radius:8px;padding:18px 22px}
.verdict-flag{background:#1f1b0d;border:1.5px solid #e3b341;border-radius:8px;padding:18px 22px}
.verdict-fail{background:#1f0d0d;border:1.5px solid #f85149;border-radius:8px;padding:18px 22px}
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
    "h200-vs-h100-training  →  expected FLAG": "sample_corpus/incoming/h200-vs-h100-training.md",
    "a100-vs-h100-llm-serving  →  expected FAIL": "sample_corpus/incoming/a100-vs-h100-llm-serving.md",
    "why-gpu-cloud-india  →  expected FAIL": "sample_corpus/incoming/why-gpu-cloud-india.md",
}

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🛡️ NeevCloud Content Quality Gate")
st.caption(
    "Automated circuit-breaker between generation and CMS. "
    "Nothing publishes without a **PASS** or a human-approved **FLAG**."
)
st.divider()

# ── Sample loader ─────────────────────────────────────────────────────────────
sample_choice = st.selectbox(
    "Load a sample post (or paste your own below)",
    ["— paste your own —"] + list(SAMPLES.keys()),
)

if sample_choice != "— paste your own —":
    p = parse_markdown(os.path.join(BASE, SAMPLES[sample_choice]))
    d_title, d_slug, d_kw = p.title, p.slug, p.primary_keyword
    d_cluster, d_class, d_body = p.cluster_id, p.content_class, p.body
else:
    d_title = d_slug = d_kw = d_cluster = ""
    d_class, d_body = "mid", ""

# ── Inputs ────────────────────────────────────────────────────────────────────
left, right = st.columns([1, 2])

with left:
    st.subheader("Post Metadata")
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
    st.subheader("Post Body (Markdown)")
    body = st.text_area(
        "body", value=d_body, height=340,
        label_visibility="collapsed", key=f"b_{sample_choice}",
    )

st.divider()
run = st.button("▶  Run Gate", type="primary", use_container_width=True)

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

    ICON  = {"PASS": "✅", "FLAG": "🟡", "FAIL": "🔴"}
    LABEL = {
        "PASS": "PASS — cleared for publish queue",
        "FLAG": "FLAG — routed to human review",
        "FAIL": "FAIL — blocked, return to generation",
    }
    CSS   = {"PASS": "verdict-pass", "FLAG": "verdict-flag", "FAIL": "verdict-fail"}
    COLOR = {"PASS": "#3fb950",      "FLAG": "#e3b341",      "FAIL": "#f85149"}

    st.subheader("Verdict")
    st.markdown(
        f'<div class="{CSS[v]}">'
        f'<span style="font-size:1.4rem;font-weight:800;color:{COLOR[v]}">'
        f'{ICON[v]} {LABEL[v]}</span></div>',
        unsafe_allow_html=True,
    )

    st.divider()
    st.subheader("Check Results")

    cols = st.columns(3)
    for i, check in enumerate(report.checks):
        with cols[i % 3]:
            with st.expander(
                f"{ICON[check.status]} **{check.name}** — {check.status}",
                expanded=(check.status != "PASS"),
            ):
                if check.reasons:
                    for r in check.reasons:
                        st.write(f"• {r}")
                else:
                    st.success("All clear.")
                if check.metrics:
                    st.json(check.metrics, expanded=False)

    st.caption(
        f"Word count: {post.word_count} · "
        f"Cluster: `{post.cluster_id}` · "
        f"Class: `{post.content_class}`"
    )
