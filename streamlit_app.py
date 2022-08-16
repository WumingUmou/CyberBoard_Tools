import streamlit as st
import json
st.title("Frame Inverter")
st.write("Upload your json file here")
read_file = st.file_uploader("upload your json", "json", False, )
if read_file is not None:
    origional_file = json.load(read_file)
    filename = ".".join(read_file.name.split(".")[:-1])
    st.write("file read success")
    targets = st.multiselect("Which page you want to invert?", ["自定义界面1/custom page1", "自定义界面2/custom page2", "自定义界面3/custom page3"],None)
    
    targets = [x.split("/")[0] for x in targets]

    if st.button("Invert"):
        new_file = origional_file.copy()
        for target in targets:
            for key, page in enumerate(new_file["page_data"]):
                if page["//"] == target:
                    st.write(page["//"])
                    frames = page["frames"]["frame_data"].copy()

                    new_frames = []
                    for frame in frames:
                        new_frame = frame.copy()
                        new_frame["frame_RGB"] = frame["frame_RGB"][::-1]
                        new_frames.append(new_frame)
                    new_file["page_data"][key]["frames"]["frame_data"] = new_frames


        st.write("Invertion finished")
        
        outfile_name =f"Inverted_{filename}.json"

        st.download_button("Download", json.dumps(new_file, indent = 4), outfile_name, "application/json")
