import os
import time

import streamlit as st
import requests


def main():
    
    st.set_page_config(page_title="Talk to your PDF")
    st.header("Talk to your PDF 💬")
    
    # upload file
    pdf = st.file_uploader("Upload your PDF", type="pdf")

    
    
    # extract the text
    if pdf is not None:
        start_time = time.time()
        response_time = time.time() - start_time
        st.write("response")


        print(response_time)
    
    res = requests.get("http://localhost:8000/get_sessions")
    st.write(res.json())
      


if __name__ == '__main__':
    main()