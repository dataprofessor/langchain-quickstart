import streamlit as st
import os
from langchain import OpenAI

st.title('🦜🔗 Quickstart App')

api_key = st.text_input('Enter OpenAI API key:', type='password')
os.environ['OPENAI_API_KEY'] = api_key

llm = OpenAI(temperature=0.7)
text = st.text_input('Enter text:', 'What are 3 key advice for learning how to code?')
st.info(llm(text))
