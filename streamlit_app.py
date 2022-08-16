import streamlit as st
import json
st.title("Frame Inverter")
st.write("Upload your json file here")
read_file = st.file_uploader("upload your json", "json", False, )
if read_file is not None:
    file = json.load(read_file)
    st.write("file read success")
    targets = st.multiselect("Which page you want to invert?", ["自定义界面1/custom page1", "自定义界面2/custom page2", "自定义界面3/custom page3"],None)
    
    targets = [x.split("/")[0] for x in targets]
    st.write(targets)
    
