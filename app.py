import streamlit as st

st.set_page_config(page_title="Security Toolkit", page_icon="🔐", layout="wide")

st.title("🔐 Security Toolkit")
st.caption("AI-powered tools to help you write and audit secure Python code.")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🛠️ Secure Code Fixer")
    st.markdown(
        "Paste a snippet of Python code and instantly get a security-hardened "
        "version with clear explanations. Great for learning and quick fixes."
    )
    st.page_link("pages/1_Secure_Code_Fixer.py", label="Open Secure Code Fixer →", icon="🛠️")

with col2:
    st.subheader("🕵️ Vulnerability Assessment")
    st.markdown(
        "Upload an entire Python project (as a .zip) and get a full security "
        "report — every file scanned, risks ranked by severity, with an overall "
        "risk score."
    )
    st.page_link("pages/2_Vulnerability_Assessment.py", label="Open Vulnerability Assessment →", icon="🕵️")

st.markdown("---")
st.caption("Built with Groq (LLaMA 3.3 70B) + Streamlit")