from __future__ import annotations

from pathlib import Path

import streamlit as st

from database import get_setting, init_db, set_setting
from ollama_client import check_ollama_health

DEFAULT_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5:1.5b"
DEFAULT_TONE = "warm"


def load_css() -> None:
	css_path = Path(__file__).resolve().parents[1] / "styles.css"
	if css_path.exists():
		st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


st.set_page_config(page_title="BibleGPT Settings", page_icon="⚙", layout="wide", initial_sidebar_state="collapsed")
init_db()
load_css()

_logo = Path(__file__).resolve().parents[1] / "assets" / "bibleGPT.png"
if _logo.exists() and _logo.stat().st_size > 0:
	st.logo(str(_logo), icon_image=str(_logo))

st.title("Settings")

current_url = get_setting("ollama_base_url", DEFAULT_BASE_URL)
current_model = get_setting("ollama_model", DEFAULT_MODEL)
current_tone = get_setting("assistant_tone", DEFAULT_TONE)

with st.form("settings_form"):
	ollama_url = st.text_input("Ollama Base URL", value=current_url)
	model_name = st.text_input("Model", value=current_model)
	tone = st.selectbox("Assistant tone", ["warm", "encouraging", "scholarly", "concise"], index=["warm", "encouraging", "scholarly", "concise"].index(current_tone) if current_tone in ["warm", "encouraging", "scholarly", "concise"] else 0)
	submitted = st.form_submit_button("Save Settings")

if submitted:
	set_setting("ollama_base_url", ollama_url.strip() or DEFAULT_BASE_URL)
	set_setting("ollama_model", model_name.strip() or DEFAULT_MODEL)
	set_setting("assistant_tone", tone)
	st.success("Settings saved")

if st.button("Test Connection"):
	ok, msg = check_ollama_health(get_setting("ollama_base_url", DEFAULT_BASE_URL))
	if ok:
		st.success(msg)
	else:
		st.error(msg)

