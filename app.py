"""
app.py
Professional Streamlit UI for the FNOL Claims Routing Agent.
"""

import io
import json
from reportlab.pdfgen import canvas
import streamlit as st

from pipeline import run_fnol_agent

st.set_page_config(page_title="Autonomous Insurance Claim", page_icon="🚗", layout="wide")

# st.title("Autonomous Insurance Claims Processing Agent")
st.markdown("""
<h1 style="text-align:center; color:#1f4e79;">
Autonomous Insurance Claims Processing Agent
</h1>

<p style="text-align:center; font-size:18px; color:#666; max-width:900px; margin:auto;">
Welcome to the AI-powered Insurance Claims Processing System.
Upload a First Notice of Loss (FNOL) document to automatically extract claim information,
validate policy details, detect missing or inconsistent data, evaluate claim risk,
and receive an intelligent routing recommendation with a complete decision report.
</p>
""", unsafe_allow_html=True)


ROUTE_COLORS = {
    "Fast-track": "🟢",
    "Manual Review": "🟡",
    "Investigation Flag": "🔴",
    "Specialist Queue": "🔵",
    "Standard Review": "⚪",
}

def get_claim_status(route):
    if route == "Fast-track":
        return "✅ APPROVED"
    elif route == "Standard Review":
        return "🟡 PENDING REVIEW"
    elif route == "Manual Review":
        return "🟠 MANUAL REVIEW"
    elif route == "Specialist Queue":
        return "🔵 SPECIALIST REVIEW"
    return "🔴 INVESTIGATION"

def get_confidence(route):
    return {
        "Fast-track":98,
        "Standard Review":90,
        "Manual Review":80,
        "Specialist Queue":72,
        "Investigation Flag":60
    }.get(route,75)

def get_risk(conf):
    if conf >= 95:
        return "LOW"
    if conf >= 80:
        return "MEDIUM"
    return "HIGH"

def create_pdf(result, claim_status, confidence, risk):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)

    y = 800
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, y, "FNOL CLAIM REPORT")

    pdf.setFont("Helvetica", 12)
    y -= 40
    pdf.drawString(50, y, f"Claim Status: {claim_status}")
    y -= 20
    pdf.drawString(50, y, f"Route: {result['recommendedRoute']}")
    y -= 20
    pdf.drawString(50, y, f"Confidence: {confidence}%")
    y -= 20
    pdf.drawString(50, y, f"Risk Level: {risk}")

    y -= 40
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(50, y, "Reasoning")
    pdf.setFont("Helvetica", 11)
    y -= 20
    pdf.drawString(50, y, result["reasoning"][:120])

    y -= 35
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(50, y, "Extracted Fields")
    pdf.setFont("Helvetica", 10)

    for k, v in result["extractedFields"].items():
        y -= 18
        if y < 50:
            pdf.showPage()
            y = 800
        pdf.drawString(55, y, f"{k}: {v}")

    pdf.save()
    buffer.seek(0)
    return buffer

st.title("📂 FNOL Claims Routing Agent")
st.caption("Upload a TXT or PDF First Notice of Loss document.")

uploaded = st.file_uploader("Upload FNOL", type=["txt","pdf"])

if uploaded:

    if uploaded.name.lower().endswith(".pdf"):
        import pdfplumber
        with pdfplumber.open(uploaded) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    else:
        text = uploaded.read().decode("utf-8", errors="ignore")

    with st.expander("Raw Document"):
        st.text(text)

    if st.button("🚀 Process Claim", type="primary"):

        with st.spinner("Running agent..."):
            result = run_fnol_agent(text)

        route = result["recommendedRoute"]
        badge = ROUTE_COLORS.get(route,"⚪")
        status = get_claim_status(route)
        confidence = get_confidence(route)
        risk = get_risk(confidence)

        st.success(f"{badge} {route}")

        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Claim Status", status)
        c2.metric("Confidence", f"{confidence}%")
        c3.metric("Risk", risk)
        c4.metric("Route", route)

        st.subheader("Decision Summary")
        st.info(result["reasoning"])

        st.subheader("Decision Reasons")
        reasons=[]

        if result["missingFields"]:
            reasons.append("Missing mandatory fields detected.")
        else:
            reasons.append("All mandatory fields are present.")

        if route=="Fast-track":
            reasons.append("Low-risk claim suitable for automatic processing.")
        elif route=="Manual Review":
            reasons.append("Requires additional human verification.")
        elif route=="Specialist Queue":
            reasons.append("Needs specialist assessment.")
        elif route=="Investigation Flag":
            reasons.append("Potential inconsistency or fraud indicators found.")
        else:
            reasons.append("Standard review required.")

        for r in reasons:
            st.write("•", r)

        st.subheader("Extracted Fields")
        st.table([
            {"Field":k,"Value":v if v else "—"}
            for k,v in result["extractedFields"].items()
        ])

        if result["missingFields"]:
            st.warning(", ".join(result["missingFields"]))
        else:
            st.success("No mandatory fields missing.")

        st.subheader("Downloads")

        clean = {
            k:v for k,v in result.items()
            if not k.startswith("_")
        }

        st.download_button(
            "⬇ Download JSON",
            json.dumps(clean, indent=4),
            file_name="claim_report.json",
            mime="application/json"
        )

        pdf = create_pdf(result, status, confidence, risk)

        st.download_button(
            "⬇ Download PDF Report",
            pdf,
            file_name="claim_report.pdf",
            mime="application/pdf"
        )

        with st.expander("Raw JSON"):
            st.code(json.dumps(clean, indent=2), language="json")
