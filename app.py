import os
import html
import requests
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

st.set_page_config(page_title="ArticleGen • Streamlit", page_icon="📰", layout="centered")
load_dotenv()

API_BASE = "https://api.corpus.swecha.org"
LOGIN_ENDPOINT = f"{API_BASE}/api/v1/auth/login"

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY") if hasattr(st, "secrets") else None
if not GEMINI_API_KEY:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY is missing. Add it in Streamlit Secrets or .env.")
else:
    genai.configure(api_key=GEMINI_API_KEY)

MODEL_ID = "gemini-1.5-flash"

ARTICLE_SYSTEM_INSTRUCTIONS = """You are an assistant that writes clean HTML articles.
Output ONLY HTML (no markdown). Structure with:
- <h1> title
- <p> paragraphs
- <h2>/<h3> subheadings
- <ul>/<ol> lists when helpful
- <strong>/<em> sparingly
Do not include <html>, <head>, or <body> tags. Return valid, minimal HTML only.
"""

if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "token_type" not in st.session_state:
    st.session_state.token_type = "Bearer"

st.sidebar.header("Authentication")
if st.session_state.access_token:
    st.sidebar.success("Logged in")
    if st.sidebar.button("Logout"):
        st.session_state.access_token = None
        st.session_state.token_type = "Bearer"
        st.experimental_rerun()
else:
    with st.sidebar.form("login_form"):
        phone = st.text_input("Phone", placeholder="+91XXXXXXXXXX")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
    if submit:
        if not phone or not password:
            st.sidebar.error("Phone and password are required.")
        else:
            try:
                r = requests.post(LOGIN_ENDPOINT, json={"phone": phone, "password": password}, timeout=15)
                if r.status_code == 200:
                    data = r.json()
                    st.session_state.access_token = data.get("access_token")
                    st.session_state.token_type = data.get("token_type", "Bearer")
                    st.sidebar.success("Logged in successfully.")
                    st.rerun()
                elif r.status_code == 422:
                    st.sidebar.error("Validation error. Check your input format.")
                else:
                    st.sidebar.error(f"Login failed ({r.status_code}).")
            except requests.RequestException as e:
                st.sidebar.error(f"Network error: {e}")

st.title("📰 ArticleGen (Streamlit)")
st.caption("Generate a full-length, well-structured article from a single title.")

if not st.session_state.access_token:
    st.info("Please log in from the left sidebar to start generating articles.")
else:
    title = st.text_input("Enter Title", placeholder="The Future of Artificial Intelligence")
    generate = st.button("Generate Article", type="primary", disabled=(not bool(GEMINI_API_KEY)))

    if generate:
        if not title.strip():
            st.error("Please enter a title.")
        else:
            prompt = (
                f"{ARTICLE_SYSTEM_INSTRUCTIONS}\n\n"
                f"Write a full-length, well-structured article for the title: \"{html.escape(title.strip())}\".\n"
                f"Target length: ~900-1200 words. Use clear subheadings and short paragraphs."
            )
            try:
                model = genai.GenerativeModel(MODEL_ID)
                with st.spinner("Generating with Gemini…"):
                    resp = model.generate_content(prompt)
                article_html = (getattr(resp, "text", "") or "").strip()
                if "<h1" not in article_html and "<p" not in article_html:
                    parts = [f"<p>{html.escape(p.strip())}</p>" for p in article_html.split("\n\n") if p.strip()]
                    article_html = "<h1>" + html.escape(title.strip()) + "</h1>" + "".join(parts)
                st.markdown(article_html, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")
