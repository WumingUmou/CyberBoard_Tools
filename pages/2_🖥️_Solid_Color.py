import streamlit as st
import json
import pickle

st.set_page_config(
    page_title="Solid Color",
    page_icon="🖥️",
)


st.title("Solid Color")
st.markdown("""
            This feature is used to make a single color fill your keyboard
            
            Great thanks to @Bennster#3408 for the idea!
            """)
st.write("Upload your json file here")


read_file = st.file_uploader("upload your json", "json", False, )
if read_file is not None:
    origional_file = json.load(read_file)
    filename = ".".join(read_file.name.split(".")[:-1])
    st.write("file read success")
    targets = st.multiselect("Which LED matrix page you want to change?", ["自定义界面1/LIGHT 1", "自定义界面2/LIGHT 2", "自定义界面3/LIGHT 3"],None)
    change = st.multiselect("Do you want to change your LED matrix or key RGB?", ["LED matrix", "key RGB"], None)
    if "LED matrix" in change:
        LED_change = True
        LED_color = st.color_picker("Pick a color for your LED matrix", "#8028F5")
    else:
        LED_change = False
    if "key RGB" in change:
        key_change = True
        key_color = st.color_picker("Pick a color for your key RGB lighting", "#8028F5")
    else:
        key_change = False
    targets = [x.split("/")[0] for x in targets]
    
    with open("mask.pkl", "rb") as f:
        mask = pickle.load(f)
    
    if st.button("Process"):
        new_file = origional_file.copy()
        for target in targets:
            for index, page in enumerate(new_file["page_data"]):
                if page["//"] == target:
                    st.write(page["//"])
                    if LED_change:
                        new_frames = [{"frame_RGB":[LED_color]*200, "frame_index":0}]
                        new_file["page_data"][index]["frames"]["frame_data"] = new_frames
                    if key_change:
                        new_key = [{"frame_RGB":[key_color]*90, "frame_index":0}]
                        for i, tf in enumerate(mask):
                            if not tf:
                                new_key[0]["frame_RGB"][i] = "#000000"
                        new_file["page_data"][index]["keyframes"]["frame_data"] = new_key

        st.write("Process finished")
        
        outfile_name =f"Solid_Color_{filename}.json"

        st.download_button("Download", json.dumps(new_file, indent = 4), outfile_name, "application/json")
