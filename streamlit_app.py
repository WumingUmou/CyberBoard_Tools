import streamlit as st

st.set_page_config(
    page_title="Welcome",
    page_icon="👋",
)

st.write("# Welcome to my AngryMiao CB config application! 👋")

st.sidebar.success("Select a feature from here.")

st.markdown(
    """
    There are some features missing under AM's official configurator. And we are here to give the community a little bit more weapons to use.
    **👈 Select a feature from the sidebar** to try it out your self!\n\n
    ### About me
    - I'm nowhere a professional programmer and this is my first open-to-public project. So if you have any ideas or thoughts, please reach out to me at @Umou#5793 in AM's discord channel.

    ### About the project
    - The project is fully open-sourced and you could find all the details and source code here from [Github](https://github.com/WumingUmou/CyberBoard_Tools)
    """
)
