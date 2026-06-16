import streamlit as st
from groq import Groq
import os

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

EXAMPLES = {
    "SQL Injection": '''import sqlite3

def get_user(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchone()''',

    "Hardcoded Password": '''import requests

PASSWORD = "admin123"
API_KEY  = "supersecretkey123"

def login():
    requests.post("https://example.com/login", data={"password": PASSWORD})''',

    "Weak Password Hashing": '''import hashlib

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()''',
}

BEGINNER_PROMPT = """You are a friendly Python security teacher helping beginner students learn secure coding.

IMPORTANT RULES:
- Only flag REAL security vulnerabilities (SQL injection, hardcoded passwords, weak hashing, command injection, etc.)
- If the code has NO security issues, say so clearly and return the original code unchanged
- Do NOT add try/except blocks, logging, or extra complexity to simple innocent code
- Do NOT over-engineer simple scripts — a print("hello") is perfectly fine!
- Keep fixes minimal — only change what is actually a security risk
- Use simple, friendly, encouraging language — no jargon!

Analyze the following Python code and respond in this EXACT format:

---VULNERABILITIES---
If real security issues exist, list them in simple terms. If none, write: "No security issues found! Your code looks good. 🎉"

---FIXED_CODE---
If there were real issues, show the fixed code with simple beginner-friendly comments. If no issues, return the original code unchanged.

---EXPLANATION---
If issues were fixed, explain in very simple terms what was wrong, why it matters, and how the fix helps. Use analogies if helpful. If no issues, give a short encouraging message.

Code to analyze:
{code}
"""

PROFESSIONAL_PROMPT = """You are an expert Python security engineer performing a professional code security audit.

Perform a thorough security analysis and respond in this EXACT format:

---VULNERABILITIES---
List all security vulnerabilities found, numbered, with:
- Vulnerability type (e.g. CWE-89, OWASP Top 10 category)
- Severity level (Critical / High / Medium / Low)
- Technical explanation of the risk

---FIXED_CODE---
The complete hardened code with inline comments referencing each fix. Apply security best practices throughout.

---EXPLANATION---
For each vulnerability:
- Root cause analysis
- Potential attack vectors and impact
- How the fix mitigates the risk
- Additional security recommendations and best practices

Code to analyze:
{code}
"""

def analyze_code(code: str, mode: str) -> dict:
    prompt_template = BEGINNER_PROMPT if mode == "🎓 Beginner" else PROFESSIONAL_PROMPT
    prompt = prompt_template.format(code=code)
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

# Mode toggle
st.markdown("### Choose Your Mode")
mode = st.radio(
    "Who are you?",
    ["🎓 Beginner", "💼 Professional"],
    horizontal=True,
)

if mode == "🎓 Beginner":
    st.success("👋 **Beginner Mode** — Simple explanations, friendly language, and helpful examples!")
else:
    st.info("💼 **Professional Mode** — Deep technical analysis, CVE references, and full security audit.")

st.markdown("---")

# Example buttons (only in beginner mode)
code_input = ""
if mode == "🎓 Beginner":
    st.subheader("📚 Try an Example")
    cols = st.columns(3)
    for i, (name, code) in enumerate(EXAMPLES.items()):
        if cols[i].button(f"🔸 {name}", use_container_width=True):
            code_input = code
    st.markdown("---")

code_input = st.text_area(
    "📋 Paste your Python code here:",
    value=code_input,
    height=250,
    placeholder="# Paste your Python code here and click Analyze!",
)

btn_label = "🔍 Analyze & Fix My Code" if mode == "🎓 Beginner" else "🔍 Run Security Audit"
analyze_btn = st.button(btn_label, type="primary", use_container_width=True)

if analyze_btn:
    if not code_input.strip():
        st.warning("Please paste some Python code first!")
    elif not os.environ.get("GROQ_API_KEY"):
        st.error("GROQ_API_KEY environment variable not set.")
    else:
        spinner_msg = "🔍 Analyzing your code... hang tight!" if mode == "🎓 Beginner" else "🔍 Running full security audit..."
        with st.spinner(spinner_msg):
            result = analyze_code(code_input, mode)

        st.markdown("---")

        # Vulnerabilities
        vuln_title = "🚨 Issues Found in Your Code" if mode == "🎓 Beginner" else "🚨 Vulnerabilities Identified"
        st.subheader(vuln_title)
        if result["vulnerabilities"]:
            st.error(result["vulnerabilities"])
        else:
            st.success("✅ No security issues found!")

        st.markdown("---")

        # Side by side
        code_title = "📝 Before & After" if mode == "🎓 Beginner" else "📝 Code Comparison"
        st.subheader(code_title)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**❌ Original Code**")
            st.code(code_input, language="python")
        with col2:
            st.markdown("**✅ Fixed & Secure Code**")
            st.code(result["fixed_code"], language="python")

        st.markdown("---")

        # Explanation
        exp_title = "💡 What Did We Learn?" if mode == "🎓 Beginner" else "💡 Technical Analysis & Recommendations"
        st.subheader(exp_title)
        st.markdown(result["explanation"])

        st.download_button(
            label="⬇️ Download Fixed Code",
            data=result["fixed_code"],
            file_name="fixed_code.py",
            mime="text/plain",
            use_container_width=True,
        )