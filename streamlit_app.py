import streamlit as st
import os
from dotenv import load_dotenv
from langchain.schema import HumanMessage
from supabase.client import Client, create_client
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.supabase import SupabaseVectorStore
from langchain.retrievers.document_compressors import DocumentCompressorPipeline
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import EmbeddingsFilter
from langchain.document_transformers import LongContextReorder
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.retrievers import RePhraseQueryRetriever
from langchain.memory import ConversationBufferMemory
# from langchain.text_splitter import CharacterTextSplitter
# from langchain.document_transformers import EmbeddingsRedundantFilter
from stream_handler import StreamHandler

load_dotenv()

st.set_page_config(page_title="🐇 WhatsUpDoc")
st.title('🐇 WhatsUpDoc')
st.sidebar.title('🐇 WhatsUpDoc')

st.sidebar.markdown('WhatsUpDoc is a **search engine** for your tech stack\'s documentation and broader knowledge base. It uses **OpenAI** to understand your questions and **Langchain** to search your tech stack\'s documentation and broader knowledge base.')

tech_stack_table_name = {
  'Tailwind CSS': 'tailwind_documents',
  'NextJS': 'nextjs_documents',
  'Stripe SDK': 'stripe_documents',
  'Langchain SDK': 'langchain_documents',
  'Supabase SDK': 'supabase_documents',
}

with st.sidebar:
  st.markdown('This is a **demo** of the WhatsUpDoc app. Please enter your OpenAI API key below to get started.')
  st.markdown('The app is currently in **alpha** and is under active development.')

  st.divider()

  tech_stack = st.selectbox(label="Choose Tech", help='Search the Documentation and Broader Knowledge Base of Your Tech Stack. ', options=('Tailwind CSS', 'NextJS', 'Stripe SDK', 'Langchain SDK', 'Supabase SDK'), label_visibility='visible')

  st.divider()

  st.text_input('Join the waitlist for early access to the app:', placeholder='e.g. kellyslater@gmail.com')

openai_api_key = os.environ.get("OPENAI_API_KEY") or st.sidebar.text_input('OpenAI API Key')

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

embeddings = OpenAIEmbeddings()

def get_vectorstore():
  vector_store = SupabaseVectorStore(
    embedding=embeddings,
    client=supabase,
    chunk_size=100,
    table_name=tech_stack_table_name[tech_stack],
    query_name=f"match_{tech_stack_table_name[tech_stack]}",
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

def get_qa_chain(compression_retriever: ContextualCompressionRetriever, chat_box):
  # Instantiate ConversationBufferMemory
  memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, output_key='answer')

  stream_handler = StreamHandler(chat_box, display_method='write')
  llm = ChatOpenAI(temperature=0.3, model='gpt-4-1106-preview', streaming=True, callbacks=[stream_handler])

  qa = ConversationalRetrievalChain.from_llm(llm=llm, retriever=compression_retriever, memory=memory, return_source_documents=True)

  return qa

def generate_response(input_text, chat_box):
  vectorstore = get_vectorstore()
  compression_retriever = get_retriever(vectorstore)
  qa_chain = get_qa_chain(compression_retriever, chat_box)

  result = qa_chain({ "question": input_text })

  st.markdown(result['answer'])


  if result['source_documents']:
    for document in result['source_documents']:
      st.markdown(document['page_content'])


st.title(tech_stack)

with st.form('my_form'):
  text = st.text_area('Enter text:', 'How do I set a gradient from teal to blue to purple to a full page background?')
  submitted = st.form_submit_button('Submit')
  if not openai_api_key.startswith('sk-'):
    st.warning('Please enter your OpenAI API key!', icon='⚠')
  if submitted and openai_api_key.startswith('sk-'):
    chat_box = st.empty()
    generate_response(text, chat_box)
