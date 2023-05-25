# 🦜🔗 Langchain - Quickstart App
```
Quickstart App built using Langchain and Streamlit
```

## Overview of the App
- Accepts input text (*e.g.* `What are 3 key advice for learning how to code?`) as prompt input using Streamlit's `st.text_area()`, then assign this to the `text` variable.
- LLM model (`llm()` is applied on the prompt input `text` to generate a response via `llm(text)`

## Demo App

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://langchain-quickstart.streamlit.app/)

## Get an OpenAI API key

You can get your own OpenAI API key by following the following instructions:
1. Go to https://platform.openai.com/account/api-keys.
2. Click on the `+ Create new secret key` button.
3. Next, enter an identifier name (optional) and click on the `Create secret key` button.
