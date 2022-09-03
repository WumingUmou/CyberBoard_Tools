import streamlit as st
from PIL import Image
import numpy as np
import pickle
import json
import io


st.title("Gif->Anime converter")
st.markdown("""
**THIS IS A TEST VERSION**

Works best when upload a gif with transparent background. Consider using other tools like 
https://onlinegiftools.com/create-transparent-gif


It is also recommended to use a third party tool like 
https://ezgif.com/
to pre-process your gif to better fit the CB.

The templet for whole keyboard is set to 1:1.8 in aspect ratio

The templet for panel only is set to 1:4 in aspect ratio

I may work on merge this transparent step indoor later, but for now, have fun!
""")


with open("template_cords.pkl", "rb") as f:
    templets = pickle.load(f)
with open("frame_led_templet.pkl", "rb") as f:
    frame_templet = pickle.load(f)

def add_margin(pil_img, top, right, bottom, left, color):
        width, height = pil_img.size
        new_width = width + right + left
        new_height = height + top + bottom
        result = Image.new("RGBA", (new_width, new_height), color,)
        result.paste(pil_img, (left, top))
        return result


def extend(im, extend_mode = False):
    if extend_mode == "panel only":
        width = 1318
        height = 1318/8
    elif extend_mode == "in-key only":
        width = 1318
        height = 1318/2.5
    elif extend_mode == "full keyboard":
        width = 1318
        height = 728

    if im.size[1]/im.size[0]>height/width:
        factor = height/im.size[1]
    else:
        factor = width/im.size[0]

    reshaped_im = im.resize((int(im.size[0]*factor), int(im.size[1]*factor)))
    left_margin = int((1318-reshaped_im.size[0])/2)
    right_margin = 1318-left_margin-reshaped_im.size[0]
    
    if extend_mode=="panel only":
        top_margin = 10
        bottom_margin = 728-top_margin-reshaped_im.size[1]
    elif extend_mode == "in-key only":
        bottom_margin = 20
        top_margin = 728-bottom_margin-reshaped_im.size[1]
    elif extend_mode == "full keyboard":
        top_margin = int((728-reshaped_im.size[1])/2)
        bottom_margin = 728-top_margin-reshaped_im.size[1]
    
    
            
    extend_im = add_margin(reshaped_im, top_margin, right_margin, bottom_margin, left_margin, (0,0,0,0))
    return extend_im

 
read_file = st.file_uploader("upload your json", "json", False, )

im_buff = st.file_uploader("upload your gif", "gif", False)

targets = st.multiselect("Which page you want to replace?", ["自定义界面1/LIGHT 1", "自定义界面2/LIGHT 2", "自定义界面3/LIGHT 3"],None)
targets = [x.split("/")[0] for x in targets]
extend_mode = st.selectbox("Which part do you want to put your gif on",["full keyboard", 'panel only', "in-key only"], index=0)

if st.button("Process") and read_file and im_buff:
    st.warning("Rendering the preview may take a few seconds to minutes based on how many frames your gif has. As long as you can see a \"Running\" sign on the top right, you should be fine.", icon="⚠️")
    
    file = json.load(read_file)
    filename = ".".join(read_file.name.split(".")[:-1])
    im = Image.open(im_buff)
    st.write(f"Your gif got {im.n_frames} frames, please wait" )


    if im.n_frames>80:
        st.warning("Your gif got more than 80 frames, which is the limit for CB to store. We will keep the first 80 frames only for your profile.")
    result = []
    for i in range(im.n_frames):
        im.seek(i)
        extended_im = extend(im.convert("RGBA"), extend_mode)
        temp = np.array(extended_im).copy()
        temp[temp[:,:,-1]==0]=[0,0,0,255]
        
        result.append(temp)
        if len(result)>80:
            break
    
    result = result[:80]
    gif = []
    frame_mapping = []
    for arr in result:
        new = np.array(Image.new("RGBA", (1318, 728), (0,0,0,255)))
        mapping = []
        for index, cord in templets.items():
            temp = []
            for (i, j) in cord:
                temp.append(arr[i, j])
            col = np.mean(temp, axis=0)
            
            for (i, j) in cord:
                new[i, j] = col
                
            mapping.append(col)
        frame_mapping.append(mapping)
        gif.append(new)

    gif_display = [Image.fromarray(arr) for arr in gif]

    buf = io.BytesIO()
    gif_display[0].save(buf,format="gif",save_all=True, append_images=gif_display[1:], optimize=False, duration=100, loop=0)
    st.image(buf.getvalue(), output_format="gif")
    frame_mapping = [['#{:02x}{:02x}{:02x}'.format(*color.astype(int)) for color in frame]for frame in frame_mapping]

    panel_frame_data = []
    board_frame_data = []

    for i, frame in enumerate(frame_mapping):
        panel_frame_data.append({
            "frame_RGB": frame[:200],
            "frame_index": i
        })
        board_data = frame[200:]
        board_frame_data.append({
            "frame_RGB": [board_data.pop(0) if x !="00" else "#000000" for x in frame_templet],
            "frame_index": i
        })


    for target in targets:
        for key, page in enumerate(file["page_data"]):
                if page["//"] == target:
                    if extend_mode in ["full keyboard", "panel only"]:
                        file["page_data"][key]["frames"]["frame_data"] = panel_frame_data
                        file["page_data"][key]["frames"]["frame_num"] = len(frame_mapping)
                    if extend_mode in ["full keyboard", "in-key only"]:
                        file["page_data"][key]["keyframes"]["frame_data"] = board_frame_data
                        file["page_data"][key]["keyframes"]["frame_num"] = len(frame_mapping)

    ######
    outfile_name =f"new_{filename}.json"
    st.download_button("Download", json.dumps(file, indent = 4), outfile_name, "application/json")