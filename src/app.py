import streamlit as st

from scraper import scrape_jumia_product
from extractor import extract_seller_claims, analyze_reviews
from comparator import compare

if "show_report" not in st.session_state:
    st.session_state.show_report = False
if "report_data" not in st.session_state:
    st.session_state.report_data = None


# ── helpers ────────────────────────────────────────────────────────────────────

def trust_label(score: int) -> tuple[str, str]:
    if score >= 75:
        return "High trust", "#05c8eb"
    if score >= 50:
        return "Mixed signals", "#ffb830"
    return "Low trust", "#ff4d6d"


VERDICT_CONFIG = {
    "CONFIRMED":    {"color": "#05c8eb", "border": "#70d6f5", "bg": "rgba(5,200,235,0.06)",   "icon": "✓"},
    "CONTRADICTED": {"color": "#ff4d6d", "border": "#ff4d6d", "bg": "rgba(255,77,109,0.06)",  "icon": "✕"},
    "MIXED":        {"color": "#ffb830", "border": "#ffb830", "bg": "rgba(255,184,48,0.06)",   "icon": "~"},
    "UNVERIFIED":   {"color": "#aaaaaa", "border": "#cccccc", "bg": "rgba(170,170,170,0.06)", "icon": "?"},
}


def sentiment_bar(pos: int, neg: int, neu: int) -> str:
    """Renders a small inline sentiment pill row."""
    return f"""
    <div style="display:flex; gap:6px; flex-wrap:wrap; margin:8px 0;">
        <span style="font-size:12px; padding:2px 8px; border-radius:4px;
                     background:rgba(5,200,235,0.1); color:#05c8eb;">
            ↑ {pos} positive
        </span>
        <span style="font-size:12px; padding:2px 8px; border-radius:4px;
                     background:rgba(255,77,109,0.1); color:#ff4d6d;">
            ↓ {neg} negative
        </span>
        <span style="font-size:12px; padding:2px 8px; border-radius:4px;
                     background:rgba(170,170,170,0.1); color:#aaa;">
            → {neu} neutral
        </span>
    </div>
    """


def sample_reviews_html(reviews: list[str]) -> str:
    """Renders sample review quotes."""
    if not reviews:
        return '<p style="font-size:12px; color:#bbb; margin:6px 0 0;">No review samples available. Customers who have bought this product have not yet posted comments</p>'
    items = "".join(
        f'<li style="font-size:13px; color:#666; margin-bottom:6px; '
        f'border-left:2px solid #e0e0e0; padding-left:10px;">'
        f'"{r}"</li>'
        for r in reviews
    )
    return f'<ul style="margin:8px 0 0 0; padding:0; list-style:none;">{items}</ul>'


def render_claimed_aspect_card(result: dict):
    verdict = result["verdict"]
    s       = VERDICT_CONFIG[verdict]
    counts  = result["sentiment_counts"]
    pos     = counts.get("positive", 0)
    neg     = counts.get("negative", 0)
    neu     = counts.get("neutral", 0)

    claims_html = "".join(
        f'<li style="font-size:13px; color:#555; margin-bottom:4px;">• {c}</li>'
        for c in result["claims"]
    )

    st.html(f"""
    <div style="padding:18px 20px; border-radius:10px; margin-bottom:14px;
                border:1px solid {s['border']}; background:{s['bg']};">

        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:12px;">
            <span style="font-weight:700; font-size:15px; color:#444; text-transform:capitalize;">
                {result['aspect'].replace('_', ' ')}
            </span>
            <span style="font-size:11px; letter-spacing:.12em; font-weight:700;
                         color:{s['color']}; padding:3px 10px;
                         border:1px solid {s['border']}; border-radius:4px;
                         background:{s['bg']};">
                {s['icon']} {verdict}
            </span>
        </div>

        <p style="font-size:11px; color:#999; margin:0 0 4px; letter-spacing:.08em;">
            SELLER CLAIMS
        </p>
        <ul style="margin:0 0 12px 0; padding:0; list-style:none;">{claims_html}</ul>

        <p style="font-size:11px; color:#999; margin:0 0 2px; letter-spacing:.08em;">
            CUSTOMER SENTIMENT
        </p>
        {sentiment_bar(pos, neg, neu)}

        <p style="font-size:11px; color:#999; margin:10px 0 2px; letter-spacing:.08em;">
            WHAT CUSTOMERS SAID
        </p>
        {sample_reviews_html(result.get('sample_reviews', []))}
    </div>
    """)


def render_unclaimed_aspect_card(unclaimed: dict):
    counts = unclaimed["sentiment_counts"]
    pos    = counts.get("positive", 0)
    neg    = counts.get("negative", 0)
    neu    = counts.get("neutral", 0)

    # color the card border based on whether the signal is mostly negative or positive
    if neg > pos:
        border_color = "#ff4d6d"
        bg_color     = "rgba(255,77,109,0.04)"
        warning      = "⚠ Seller didn't address this"
    elif pos > neg:
        border_color = "#05c8eb"
        bg_color     = "rgba(5,200,235,0.04)"
        warning      = "✦ Customers brought this up positively"
    else:
        border_color = "#ffb830"
        bg_color     = "rgba(255,184,48,0.04)"
        warning      = "~ Mixed — seller didn't address this"

    st.html(f"""
    <div style="padding:18px 20px; border-radius:10px; margin-bottom:14px;
                border:1px solid {border_color}; background:{bg_color};">

        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:12px;">
            <span style="font-weight:700; font-size:15px; color:#444; text-transform:capitalize;">
                {unclaimed['aspect'].replace('_', ' ')}
            </span>
            <span style="font-size:11px; color:{border_color}; font-weight:600;">
                {warning}
            </span>
        </div>

        <p style="font-size:11px; color:#999; margin:0 0 2px; letter-spacing:.08em;">
            CUSTOMER SENTIMENT
        </p>
        {sentiment_bar(pos, neg, neu)}

        <p style="font-size:11px; color:#999; margin:10px 0 2px; letter-spacing:.08em;">
            WHAT CUSTOMERS SAID
        </p>
        {sample_reviews_html(unclaimed.get('sample_reviews', []))}
    </div>
    """)


# ── landing page ───────────────────────────────────────────────────────────────

if not st.session_state.show_report:
    st.html("""
    <div style="margin-bottom:32px;">
        <span style="font-size:12px; letter-spacing:.15em;
               padding:4px 10px; border:1px solid #70d6f5;
               border-radius:4px; background:#ffff; color:#05c8eb;">ClaimCheck</span>
        <h1 style="font-weight:700; font-size:30px; color:#444;
                   line-height:1.2; margin-top:10px;">
            Does this seller deliver what they promise?
        </h1>
        <p style="color:#888; font-size:14px; margin-top:8px;">
            Paste a Jumia product URL. We compare what the seller claims
            against what customers actually say.
        </p>
    </div>
    """)

    product_url = st.text_input(
        label="Product URL",
        placeholder="https://www.jumia.com.ng/...",
        label_visibility="collapsed"
    )

    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        analyze = st.button("Analyze →", use_container_width=True)
    with col_info:
        st.markdown(
            '<p style="font-size:13px; font-weight:500; color:#7a7a7a; margin-top:10px;">Based on first 10 reviews</p>',
            unsafe_allow_html=True
        )

    if analyze:
        if not product_url or not product_url.startswith("https://www.jumia.com.ng/"):
            st.error("Please enter a valid Jumia product URL.")
        else:
            try:
                with st.spinner("Scraping product data..."):
                    product = scrape_jumia_product(product_url=product_url)
            except Exception as e:
                st.error("Something went wrong. Try again")
                st.stop()

            if not product:
                st.error("Scraping failed. Check the URL and try again.")
                st.stop()

            with st.spinner("Extracting seller claims..."):
                claims = extract_seller_claims(product["description"])

            with st.spinner("Analyzing customer reviews..."):
                analyzed_reviews = analyze_reviews(product["reviews"])

            with st.spinner("Comparing claims vs reviews..."):
                comparison = compare(claims=claims, analyzed_reviews=analyzed_reviews)

            st.session_state.report_data = {
                "product":          product,
                "claims":           claims,
                "analyzed_reviews": analyzed_reviews,
                "comparison":       comparison,
            }
            st.session_state.show_report = True
            st.rerun()


# ── report page ────────────────────────────────────────────────────────────────

else:
    data        = st.session_state.report_data
    product     = data["product"]
    comparison  = data["comparison"]
    summary     = comparison["summary"]
    score       = comparison["trust_score"]
    label, color = trust_label(score)

    st.button(
        "← Analyze another product",
        on_click=lambda: st.session_state.update(show_report=False, report_data=None)
    )

    st.html(f"""
    <div style="margin-bottom:24px;">
        <span style="font-size:11px; letter-spacing:.15em;
               padding:4px 10px; border:1px solid #70d6f5;
               border-radius:4px; background:#ffff; color:#05c8eb;">CLAIM CHECK</span>
        <h1 style="font-weight:700; font-size:28px; color:#444;
                   line-height:1.2; margin-top:10px;">
            Does this seller deliver what they promise?
        </h1>
        <p style="color:#888; font-size:14px; margin-top:4px;">{product['product_name']}</p>
    </div>
    """)

    # ── trust score + summary metrics ──────────────────────────────────────────
    col_score, col_conf, col_contra, col_mixed, col_unver = st.columns(5)
    with col_score:
        st.html(f"""
        <div style="background:#f9f9f9; border-radius:8px; padding:14px 16px; text-align:center;">
            <p style="font-size:11px; color:#999; margin:0 0 4px; letter-spacing:.08em;">TRUST SCORE</p>
            <p style="font-size:28px; font-weight:700; color:{color}; margin:0;">{score}</p>
            <p style="font-size:11px; color:{color}; margin:4px 0 0;">{label}</p>
        </div>
        """)
    with col_conf:
        st.metric("Confirmed",    summary["confirmed"],    border=True)
    with col_contra:
        st.metric("Contradicted", summary["contradicted"], border=True)
    with col_mixed:
        st.metric("Mixed",        summary["mixed"],        border=True)
    with col_unver:
        st.metric("Unverified",   summary["unverified"],   border=True)

    st.write("")

    # ── claimed aspects ────────────────────────────────────────────────────────
    st.markdown("### What the seller claimed")
    st.caption("Each aspect the seller described, checked against what customers actually experienced.")
    st.write("")

    if comparison["results"]:
        for result in comparison["results"]:
            render_claimed_aspect_card(result)
    else:
        st.info("No seller claims could be extracted from the product description.")

    # ── unclaimed aspects ──────────────────────────────────────────────────────
    if comparison["unclaimed_aspects"]:
        st.write("")
        st.markdown("### What the seller didn't mention")
        st.caption("Aspects customers brought up in reviews that the seller never addressed in the description.")
        st.write("")

        for unclaimed in comparison["unclaimed_aspects"]:
            render_unclaimed_aspect_card(unclaimed)

    # ── raw data expander ──────────────────────────────────────────────────────
    with st.expander("Raw data"):
        st.subheader("Seller claims")
        st.json(data["claims"])
        st.subheader("Review sentiments")
        st.json(data["analyzed_reviews"])
        st.subheader("Full comparison output")
        st.json(data["comparison"])