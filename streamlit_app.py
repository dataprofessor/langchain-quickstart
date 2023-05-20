import streamlit as st
import os
from langchain import OpenAI

st.title('🦜🔗 Quickstart App')

def generate_response(input_text):
  os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
  llm = OpenAI(temperature=0.7)
  st.info(llm(input_text))

with st.form('my_form'):
  text = st.text_area('Enter text:', 'What are 3 key advice for learning how to code?')
  submitted = st.form_submit_button('Submit')
  if submitted:
    generate_response(text)
