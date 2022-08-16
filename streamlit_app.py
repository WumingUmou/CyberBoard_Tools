import streamlit as st
import json
st.title("Frame Inverter")
st.write("Upload your json file here")
read_file = st.file_uploader("upload your json", "json", False, )
if read_file is not None:
    file = json.load(file)
    st.write("file read success")