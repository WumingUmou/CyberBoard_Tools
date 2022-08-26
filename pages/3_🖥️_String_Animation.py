import io
from PIL import Image, ImageDraw
import streamlit as st
import pickle
import numpy as np
import json


def display(colored_frames):
    '''return a CB LED config as gif (binary)'''
    gif=[]
    for frame in colored_frames:
        im = np.zeros((50,400,3), dtype=np.uint8) 
        i=0
        for row in range (5):
            for col in range(40):

                h = frame[i]
                R = int(h[1:3],16) 
                G = int(h[3:5],16) 
                B = int(h[5:7],16) 
                im[row*10:(row+1)*10,col*10:(col+1)*10] = (R, G, B)
                i = i+1
        img = Image.fromarray(im, 'RGB')
        gif.append(img)
        buf = io.BytesIO()
        gif[0].save(buf,format="gif",
                       save_all=True, append_images=gif[1:], optimize=False, duration=speed, loop=0)
    return buf.getvalue()

# read in templets
with open("num_templet.pkl", "rb") as f:
    num_templet = pickle.load(f, encoding='utf-8')
with open("alphabet_templet.pkl", "rb") as f:
    alphabet_templet = pickle.load(f, encoding='utf-8')
with open("symbol_templet.pkl", "rb") as f:
    symbol_templet = pickle.load(f, encoding='utf-8')

templets = [alphabet_templet, num_templet, symbol_templet]
templet = dict()
for t in templets:
    templet.update(t)



st.title("String to Animation")
st.markdown("This feature is used to convert a string to a Animation on CB")
st.write("Upload your json file here")
read_file = st.file_uploader("upload your json", "json", False, )

s = st.text_input("String wants to be transfered")
st.markdown("""
Supported characters:

(All characters will be automaticly transformed to upper case, lower case isn't supported in the font yet)

`ABCDEFGHIJKLMNOPQRSTUVWXYZ`

`1234567890`

`'"~,.!?@#%^*()+-=[]{}\/<>♥♡ `
""")

interval = int(st.number_input("Interval between characters", value=1, step=1))
highlight_color = st.color_picker("Color for your word", value="#fb2424")
background_color = st.color_picker("Color for your background")
speed = st.slider("Speed for your animation (interval between frames, in ms)", min_value=34, max_value=100, value=80)
if read_file is not None:
    origional_file = json.load(read_file)
    filename = ".".join(read_file.name.split(".")[:-1])
    st.write("file read success")
    targets = st.multiselect("Which page you want to replace?", ["自定义界面1/LIGHT 1", "自定义界面2/LIGHT 2", "自定义界面3/LIGHT 3"],None)
    
    targets = [x.split("/")[0] for x in targets]

    result = None
    for c in s.upper():
        if result is None:
            result = templet[c]
        else:
            result = np.concatenate([result, np.zeros((5, interval)), templet[c]], axis=1)


    constant = st.checkbox("Do you want the frame to be constant")

    

    if st.button("Process"):
        if constant and result.shape[1]>40:
            st.write("Your string is too long for constant frame, try rolling")

        if constant:
            x = (40-result.shape[1])//2
            try:
                results = [np.concatenate([np.zeros((5, x)), result, np.zeros((5, 40-x-result.shape[1]))], axis=1)]
            except:
                results = []
        else:
            results = []
            result = np.concatenate([np.zeros((5, 40)), result, np.zeros((5, 39))], axis=1).astype(int)
            for i in range(result.shape[1]-39):
                results.append(result[:5, i:i+40])
        if len(results)>80:
            st.warning(f"Your string is too long at {len(results)+40} frames, try something shorter.\nWe have compressed it to the first 80 frames.", icon="⚠️")
            results = results[41:121]
        if len(results)==0:
            st.error("Your string is too long for constant frame", icon="🚨")
        else:
            results = results[:80]

            colors = {1:highlight_color, 0:background_color}
            st.write(len(results))
            st.write("The preview gif may take a few seconds to be generated while we process your string")
            
            colored_frames = []
            for frame in results:
                colored_frames.append([colors[x] for x in frame.reshape(1,-1).tolist()[0]])

        new_frames = []
        i=0
        for frame in colored_frames:
            new_frames.append({"frame_RGB":frame, "frame_index":i})
            i+=1
        
        new_file = origional_file.copy()
        for target in targets:
            for key, page in enumerate(new_file["page_data"]):
                if page["//"] == target:
                    st.write(page["//"])
                    new_file["page_data"][key]["frames"]["frame_data"] = new_frames
                    new_file["page_data"][key]["frames"]["frame_num"]=len(colored_frames)
                    new_file["page_data"][key]["speed_ms"]=speed
        st.image(display(colored_frames), output_format="gif")
            
        st.write("Process finished")
        
        outfile_name =f"new_{filename}.json"

        st.download_button("Download", json.dumps(new_file, indent = 4), outfile_name, "application/json")
