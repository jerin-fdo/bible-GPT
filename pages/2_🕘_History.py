from __future__ import annotations

from pathlib import Path

import streamlit as st

from database import get_recent_chats, init_db, save_message


def load_css() -> None:
	css_path = Path(__file__).resolve().parents[1] / "styles.css"
	if css_path.exists():
		st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


st.set_page_config(page_title="BibleGPT History", page_icon="🕘", layout="wide", initial_sidebar_state="collapsed")
init_db()
load_css()

_logo = Path(__file__).resolve().parents[1] / "assets" / "bibleGPT.png"
if _logo.exists() and _logo.stat().st_size > 0:
	st.logo(str(_logo), icon_image=str(_logo))

st.title("History")

limit = st.slider("Show recent chats", min_value=10, max_value=100, value=30, step=10)
rows = get_recent_chats(limit=limit)

if not rows:
	st.info("No chat history yet.")

for row in rows:
	chat_title = row["user_message"][:80].strip() or "(empty question)"
	with st.expander(f"#{row['id']} | {chat_title}"):
		st.markdown("<div class='bible-card'>", unsafe_allow_html=True)
		st.markdown(f"**Asked:** {row['user_message']}")
		st.markdown(f"**Response:**\n\n{row['assistant_message']}")
		st.caption(f"Created at: {row['created_at']}")

		note_key = f"hist_note_{row['id']}"
		note = st.text_input("Save note", key=note_key)
		if st.button("Save this response", key=f"save_btn_{row['id']}"):
			save_message(int(row["id"]), note)
			st.success("Saved")
		st.markdown("</div>", unsafe_allow_html=True)

