import streamlit as st
import os
from langchain import OpenAI

st.title('🦜🔗 Quickstart App')

api_key = st.text_input('Enter OpenAI API key:', type='password')

def generate_response(input_text):
  llm = OpenAI(temperature=0.7)
  os.environ['OPENAI_API_KEY'] = api_key
  st.info(llm(input_text))

with st.form('my_form'):
  text = st.text_area('Enter text:', 'What are 3 key advice for learning how to code?')
  submitted = st.form_submit_button('Submit')
  if submitted:
    if api_key == '':
      generate_response(text)
    else:
      st.error('Please enter OpenAI API key', icon='⚠️')
