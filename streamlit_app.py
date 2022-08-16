import streamlit as st
import json
st.title("Frame Inverter")
st.write("Upload your json file here")
file = st.file_uploader("upload your json", "json", False, )
if file is not None:
    st.write(json.load(file))