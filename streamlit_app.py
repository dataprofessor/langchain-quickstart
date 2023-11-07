import streamlit as st
import os
from dotenv import load_dotenv
from langchain.llms import OpenAI
from supabase.client import Client, create_client
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.supabase import SupabaseVectorStore
from langchain.retrievers.document_compressors import DocumentCompressorPipeline
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import EmbeddingsFilter
from langchain.document_transformers import LongContextReorder
from langchain.chat_models import ChatOpenAI
# from langchain.chat_models import OpenAI
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.retrievers import RePhraseQueryRetriever
from langchain.memory import ConversationBufferMemory
# from langchain.text_splitter import CharacterTextSplitter
# from langchain.document_transformers import EmbeddingsRedundantFilter

load_dotenv()

st.set_page_config(page_title="🦜🔗 Quickstart App")
st.title('🦜🔗 Quickstart App')

openai_api_key = st.sidebar.text_input('OpenAI API Key')

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

embeddings = OpenAIEmbeddings()

def get_vectorstore():
  vector_store = SupabaseVectorStore(
    embedding=embeddings,
    client=supabase,
    chunk_size=100,
    table_name="tailwind_documents",
    query_name="match_tailwind_documents",
  )

  return vector_store

def get_retriever(vector_store: SupabaseVectorStore):
  reordering = LongContextReorder()
  relevant_filter = EmbeddingsFilter(embeddings=embeddings, similarity_threshold=0.76)

  # TODO: Maybe add these back in later, or other Filters
  # splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=0, separator=". ")
  # redundant_filter = EmbeddingsRedundantFilter(embeddings=embeddings)

  pipeline_compressor = DocumentCompressorPipeline(
      transformers=[
          # splitter,
          # redundant_filter,
          relevant_filter,
          reordering
      ]
  )

  compression_retriever = ContextualCompressionRetriever(base_compressor=pipeline_compressor, base_retriever=vector_store.as_retriever())

  return compression_retriever

def get_qa_chain(compression_retriever: ContextualCompressionRetriever):
  # Instantiate ConversationBufferMemory
  memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, output_key='answer')

  DEFAULT_TEMPLATE = """You are an assistant tasked with taking a natural language \
  query from a user and converting it into a query for a vectorstore. \
  In this process, you strip out information that is not relevant for \
  the retrieval task. Here is the user query: {question}"""

  llm = ChatOpenAI(temperature=0)
  # retriever_from_llm = RePhraseQueryRetriever.from_llm(
  #     retriever=compression_retriever, llm=llm
  # )
  # docs = retriever_from_llm.get_relevant_documents("How do I load documents from Hacker News?")

  qa = ConversationalRetrievalChain.from_llm(llm=llm, retriever=compression_retriever, memory=memory, return_source_documents=True)

  return qa

def generate_response(input_text):
  # llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
  vectorstore = get_vectorstore()
  compression_retriever = get_retriever(vectorstore)
  qa_chain = get_qa_chain(compression_retriever)

  st.info(qa_chain({ "question": input_text }))

with st.form('my_form'):
  text = st.text_area('Enter text:', 'What are the three key pieces of advice for learning how to code?')
  submitted = st.form_submit_button('Submit')
  if not openai_api_key.startswith('sk-'):
    st.warning('Please enter your OpenAI API key!', icon='⚠')
  if submitted and openai_api_key.startswith('sk-'):
    generate_response(text)
