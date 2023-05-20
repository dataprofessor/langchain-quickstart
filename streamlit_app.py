import streamlit as st
import os
from langchain import OpenAI

st.title('🦜🔗 Quickstart App')

api_key = st.text_input('Enter OpenAI API key:', type='password')
if api_key:
  os.environ['OPENAI_API_KEY'] = api_key

with st.form('my_form'):
  llm = OpenAI(temperature=0.7)
  text = st.text_area('Enter text:', 'What are 3 key advice for learning how to code?')
  submitted = st.form_submit_button('Submit')
  if submitted:
    st.info(llm(text))
