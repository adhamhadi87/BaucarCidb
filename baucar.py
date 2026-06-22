import streamlit as st

st.set_page_config(
    page_title="Baucar CIDB",
    page_icon="📁",
    layout="wide"
)

st.markdown("""
<div style="text-align:center; padding-top:100px;">
    <h1 style="font-size:60px;">
        Baucar CIDB
    </h1>
    <p style="font-size:24px; color:gray;">
        Sistem Pengurusan Keluar Masuk Baucar
    </p>
</div>
""", unsafe_allow_html=True)

st.stop()