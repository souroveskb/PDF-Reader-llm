import os
import time
import ast
import streamlit as st
import requests


def main():
    
    st.set_page_config(page_title="Talk to your PDF")
    st.header("Talk to your PDF!")
    
    res = requests.get("http://localhost:8000/get_sessions")
    # st.write(res.json())
    session_list_api = ast.literal_eval(res.text)

    session_list = ["new session"]
    session_list.extend(session_list_api)

    option = st.selectbox("Select a Session", session_list)
    st.write(option)

    if option is "new session":
        # upload file
        pdf = st.file_uploader("Upload your PDF", type="pdf")
        
        if pdf is not None:
            session_name = requests.post(f"http://localhSost:8000/upload/{option}/", pdf)
            st.write(session_name.json())
            
    else:
        res = requests.get(f"http://localhost:8000/list_pdfs/{option}")
        pdf_list_api = ast.literal_eval(res.text)
        pdf_option = st.selectbox("Select a pdf to talk to: ", pdf_list_api)
        st.write(pdf_option)

        query = st.text_input("Ask a question about the PDF:")

        req_response = requests.get(f"http://localhost:8000/get_response/{option}/{pdf_option}/{query}")

        st.write(req_response.text)




        
    


if __name__ == '__main__':
    main()