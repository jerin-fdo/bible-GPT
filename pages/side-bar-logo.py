from pathlib import Path
import streamlit as st

# Project root
ROOT_DIR = Path(__file__).resolve().parents[1]

# Logo path
display_icon_path = ROOT_DIR / "assets" / "bibleGPT.png"

with st.sidebar:
    # Display logo if it exists
    if display_icon_path.exists():
        st.image(str(display_icon_path), width=120)

    # App title and subtitle
    st.markdown(
        """
        <h2 style="margin-top:10px; margin-bottom:0; text-align:center;">
            📖 BibleGPT
        </h2>
        <p style="text-align:center; color:#777; font-size:14px;">
            Scripture-centered AI Assistant
        </p>
        <hr>
        """,
        unsafe_allow_html=True,
    )