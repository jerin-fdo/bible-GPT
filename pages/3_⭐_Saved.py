from __future__ import annotations

from pathlib import Path

import streamlit as st

from database import delete_saved_message, get_saved_messages, init_db


def load_css() -> None:
	css_path = Path(__file__).resolve().parents[1] / "styles.css"
	if css_path.exists():
		st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


st.set_page_config(page_title="BibleGPT Saved", page_icon="⭐", layout="wide", initial_sidebar_state="collapsed")
init_db()
load_css()

_logo = Path(__file__).resolve().parents[1] / "assets" / "bibleGPT.png"
if _logo.exists() and _logo.stat().st_size > 0:
	st.logo(str(_logo), icon_image=str(_logo))

st.title("Saved Responses")

rows = get_saved_messages()
if not rows:
	st.info("No saved responses yet.")

for row in rows:
	with st.container(border=True):
		st.markdown(f"**Question:** {row['user_message']}")
		st.markdown(f"**Response:**\n\n{row['assistant_message']}")
		if row["note"]:
			st.caption(f"Note: {row['note']}")
		st.caption(f"Saved at: {row['saved_at']}")
		if st.button("Delete", key=f"del_{row['save_id']}"):
			delete_saved_message(int(row["save_id"]))
			st.rerun()

