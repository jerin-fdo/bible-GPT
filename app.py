from __future__ import annotations

from pathlib import Path

import streamlit as st

from database import add_chat, get_setting, init_db, save_message, set_setting
from ollama_client import check_ollama_health, stream_chat
from prompts import build_system_prompt, build_user_prompt

DEFAULT_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5:1.5b"
DEFAULT_TONE = "warm"
ASSETS_DIR = Path(__file__).parent / "assets"
TOP_ICON_PATH = ASSETS_DIR / "bibleGPT.png"
FALLBACK_LOGO_PATH = ASSETS_DIR / "logo.png"


def load_css() -> None:
	css_path = Path(__file__).parent / "styles.css"
	if css_path.exists():
		st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def ensure_defaults() -> None:
	if not get_setting("ollama_base_url"):
		set_setting("ollama_base_url", DEFAULT_BASE_URL)
	if not get_setting("ollama_model"):
		set_setting("ollama_model", DEFAULT_MODEL)
	if not get_setting("assistant_tone"):
		set_setting("assistant_tone", DEFAULT_TONE)


page_icon = str(TOP_ICON_PATH) if TOP_ICON_PATH.exists() and TOP_ICON_PATH.stat().st_size > 0 else "📖"
st.set_page_config(page_title="BibleGPT", page_icon=page_icon, layout="wide", initial_sidebar_state="collapsed")
init_db()
ensure_defaults()
load_css()

_logo = TOP_ICON_PATH if TOP_ICON_PATH.exists() and TOP_ICON_PATH.stat().st_size > 0 else FALLBACK_LOGO_PATH
if _logo.exists() and _logo.stat().st_size > 0:
	st.logo(str(_logo), icon_image=str(_logo))

display_icon_path = None
if TOP_ICON_PATH.exists() and TOP_ICON_PATH.stat().st_size > 0:
	display_icon_path = TOP_ICON_PATH
elif FALLBACK_LOGO_PATH.exists() and FALLBACK_LOGO_PATH.stat().st_size > 0:
	display_icon_path = FALLBACK_LOGO_PATH

base_url = get_setting("ollama_base_url", DEFAULT_BASE_URL)
model = get_setting("ollama_model", DEFAULT_MODEL)
tone = get_setting("assistant_tone", DEFAULT_TONE)

ok, health_msg = check_ollama_health(base_url)

if "chat_messages" not in st.session_state:
	st.session_state.chat_messages = []

# Hide hero section once conversation starts (ChatGPT-like)
if not st.session_state.chat_messages:
	hero_col = st.columns([1, 2, 1])[1]
	with hero_col:
		if display_icon_path:
			st.image(str(display_icon_path), width=120)
		st.markdown("<h1 class='home-title'>BibleGPT</h1>", unsafe_allow_html=True)
		st.markdown(
			"<p class='home-subtitle'>Scripture-centered AI assistant powered by your local Ollama model</p>",
			unsafe_allow_html=True,
		)
		if ok:
			st.success(f"{health_msg} | Model: {model}")
		else:
			st.warning(health_msg)

for msg in st.session_state.chat_messages:
	with st.chat_message(msg["role"]):
		st.markdown(msg["content"])

user_text = st.chat_input("Message BibleGPT")

if user_text and user_text.strip():
	user_text = user_text.strip()
	st.session_state.chat_messages.append({"role": "user", "content": user_text})
	with st.chat_message("user"):
		st.markdown(user_text)

	assistant_full = ""
	with st.chat_message("assistant"):
		holder = st.empty()
		try:
			for chunk in stream_chat(
				model=model,
				system_prompt=build_system_prompt(tone),
				user_prompt=build_user_prompt(user_text),
				base_url=base_url,
			):
				assistant_full += chunk
				holder.markdown(assistant_full)
		except Exception as exc:
			assistant_full = f"I could not reach Ollama. Details: {exc}"
			holder.error(assistant_full)

	st.session_state.chat_messages.append({"role": "assistant", "content": assistant_full})
	st.session_state.last_chat_id = add_chat(user_text, assistant_full)

if st.session_state.get("last_chat_id"):
	with st.expander("Save latest response"):
		note = st.text_input("Optional note", key="save_note_latest")
		if st.button("Save"):
			save_message(int(st.session_state.last_chat_id), note)
			st.success("Saved")

