# 📰 ArticleGen (Streamlit) — With Swecha Login

This is a Streamlit version of ArticleGen with Swecha Corpus API login (POST /api/v1/auth/login) and Gemini text generation.

## Run Locally
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# Either .env or Streamlit secrets
echo GEMINI_API_KEY=AIza... > .env
streamlit run app.py
```

## Deploy on Streamlit Cloud
- Add `GEMINI_API_KEY` in app secrets.
- Point to `app.py`.
