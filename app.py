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

PROMPT_TEMPLATE = """You are a friendly Python security teacher helping beginner students learn secure coding.

IMPORTANT RULES:
- Only flag REAL security vulnerabilities (SQL injection, hardcoded passwords, weak hashing, command injection, etc.)
- If the code has NO security issues, say so clearly and return the original code unchanged
- Do NOT add try/except blocks, logging, or extra complexity to simple innocent code
- Do NOT over-engineer simple scripts — a print("hello") is perfectly fine!
- Keep fixes minimal — only change what is actually a security risk

Analyze the following Python code and respond in this EXACT format:

---VULNERABILITIES---
If real security issues exist, list them simply. If none, write: "No security issues found! Your code looks good."

---FIXED_CODE---
If there were real issues, show the fixed code with simple comments. If no issues, return the original code unchanged.

---EXPLANATION---
If issues were fixed, explain in simple beginner-friendly terms what was wrong and why. If no issues, give a short encouraging message.

Code to analyze:
{code}
"""

def analyze_code(code: str) -> dict:
    prompt = PROMPT_TEMPLATE.format(code=code)
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

st.set_page_config(page_title="Secure Code Fixer for Students", page_icon="🔐", layout="wide")

st.title("🔐 Secure Code Fixer")
st.caption("A learning tool for students — paste your Python code and learn how to make it secure!")

st.info("👋 **New to security?** Try one of the examples below to see how common mistakes are fixed!")

# Example buttons
st.subheader("📚 Try an Example")
cols = st.columns(3)
code_input = ""
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

analyze_btn = st.button("🔍 Analyze & Fix My Code", type="primary", use_container_width=True)

if analyze_btn:
    if not code_input.strip():
        st.warning("Please paste some Python code first or try one of the examples above!")
    elif not os.environ.get("GROQ_API_KEY"):
        st.error("GROQ_API_KEY environment variable not set.")
    else:
        with st.spinner("🔍 Analyzing your code... hang tight!"):
            result = analyze_code(code_input)

        st.markdown("---")

        # Vulnerabilities
        st.subheader("🚨 Issues Found in Your Code")
        if result["vulnerabilities"]:
            st.error(result["vulnerabilities"])
        else:
            st.success("✅ Great job! No major security issues found.")

        st.markdown("---")

        # Side by side
        st.subheader("📝 Before & After")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**❌ Your Original Code**")
            st.code(code_input, language="python")
        with col2:
            st.markdown("**✅ Fixed & Secure Code**")
            st.code(result["fixed_code"], language="python")

        st.markdown("---")

        # Explanation
        st.subheader("💡 What Did We Learn?")
        st.markdown(result["explanation"])

        st.download_button(
            label="⬇️ Download Fixed Code",
            data=result["fixed_code"],
            file_name="fixed_code.py",
            mime="text/plain",
            use_container_width=True,
        )