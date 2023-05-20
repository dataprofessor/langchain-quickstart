import streamlit as st
import os
from langchain import OpenAI

st.title('🦜🔗 Quickstart App')

with st.form('my_form'):
  llm = OpenAI(temperature=0.7)
  api_key = st.text_input('Enter OpenAI API key:', type='password')
  text = st.text_area('Enter text:', 'What are 3 key advice for learning how to code?')
  submitted = st.form_submit_button('Submit')
  if submitted:
    os.environ['OPENAI_API_KEY'] = api_key
    st.info(llm(text))
