import streamlit as st
from groq import Groq
import os
 
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
 
DEPTH_GUIDE = {
    "Quick": "Identify and fix only the most critical security vulnerabilities.",
    "Standard": "Identify and fix all security vulnerabilities with clear explanations.",
    "Deep": "Perform an exhaustive security audit, fix all issues, and provide detailed remediation steps and best practices.",
}
 
PROMPT_TEMPLATE = """You are an expert Python security engineer.
 
Analysis depth: {depth_guide}
 
Analyze the following Python code for security vulnerabilities and return your response in this exact format:
 
---VULNERABILITIES---
List each vulnerability found, numbered, with a brief explanation.
 
---FIXED_CODE---
The complete fixed Python code with security issues resolved. Add inline comments where changes were made.
 
---EXPLANATION---
A clear explanation of what was changed and why, numbered to match the vulnerabilities.
 
Code to analyze:
{code}
"""
 
def analyze_code(code: str, depth: str) -> dict:
    prompt = PROMPT_TEMPLATE.format(
        depth_guide=DEPTH_GUIDE[depth],
        code=code
    )
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    result = response.choices[0].message.content
 
    sections = {"vulnerabilities": "", "fixed_code": "", "explanation": ""}
 
    if "---VULNERABILITIES---" in result:
        sections["vulnerabilities"] = result.split("---VULNERABILITIES---")[1].split("---FIXED_CODE---")[0].strip()
    if "---FIXED_CODE---" in result:
        sections["fixed_code"] = result.split("---FIXED_CODE---")[1].split("---EXPLANATION---")[0].strip()
        # Strip markdown code fences if present
        if sections["fixed_code"].startswith("```"):
            sections["fixed_code"] = "\n".join(sections["fixed_code"].split("\n")[1:])
        if sections["fixed_code"].endswith("```"):
            sections["fixed_code"] = "\n".join(sections["fixed_code"].split("\n")[:-1])
    if "---EXPLANATION---" in result:
        sections["explanation"] = result.split("---EXPLANATION---")[1].strip()
 
    return sections
 
 
# ── UI ──────────────────────────────────────────────────────────────────────
 
st.set_page_config(page_title="Secure Code Fixer", page_icon="🔐", layout="wide")
 
st.title("🔐 Secure Code Fixer")
st.caption("Paste your Python code below and get a security-hardened version powered by AI.")
 
with st.sidebar:
    st.header("⚙️ Settings")
    depth = st.selectbox("Analysis Depth", ["Quick", "Standard", "Deep"], index=1)
    st.markdown("---")
    st.markdown("**Depth Guide:**")
    st.info(DEPTH_GUIDE[depth])
    st.markdown("---")
    st.markdown("Made with Groq + Streamlit")
 
code_input = st.text_area(
    "📋 Paste your Python code here:",
    height=300,
    placeholder="# Paste your vulnerable Python code here...",
)
 
analyze_btn = st.button("🔍 Analyze & Fix", type="primary", use_container_width=True)
 
if analyze_btn:
    if not code_input.strip():
        st.warning("Please paste some Python code first.")
    elif not os.environ.get("GROQ_API_KEY"):
        st.error("GROQ_API_KEY environment variable not set.")
    else:
        with st.spinner("Analyzing your code for vulnerabilities..."):
            result = analyze_code(code_input, depth)
 
        st.markdown("---")
 
        # Vulnerabilities
        st.subheader("🚨 Vulnerabilities Found")
        if result["vulnerabilities"]:
            st.error(result["vulnerabilities"])
        else:
            st.success("No vulnerabilities detected!")
 
        st.markdown("---")
 
        # Side by side: original vs fixed
        st.subheader("📝 Code Comparison")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**❌ Original (Vulnerable)**")
            st.code(code_input, language="python")
        with col2:
            st.markdown("**✅ Fixed (Secure)**")
            st.code(result["fixed_code"], language="python")
 
        st.markdown("---")
 
        # Explanation
        st.subheader("💡 What Was Fixed & Why")
        st.markdown(result["explanation"])
 
        # Download fixed code
        st.download_button(
            label="⬇️ Download Fixed Code",
            data=result["fixed_code"],
            file_name="fixed_code.py",
            mime="text/plain",
            use_container_width=True,
        )
 