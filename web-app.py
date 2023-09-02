import streamlit as st
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS, Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.llms import OpenAI as OpenAI_llm
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain,RetrievalQA
from langchain.memory import ConversationBufferMemory
from langchain.document_loaders import PyPDFLoader, TextLoader, WebBaseLoader
from langchain.prompts.chat import ChatPromptTemplate,HumanMessagePromptTemplate,SystemMessagePromptTemplate
# from langchain.chains.qa_with_sources import load_qa_with_sources_chain,BaseCombineDocumentsChain
import os
import chromadb
import tempfile
import requests
import openai
from bs4 import BeautifulSoup
from urllib.parse import urlparse

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def assistant(url):


    question=st.text_input("Ask your Question")

    if st.button("Submit",type="primary"):
        ABS_PATH: str = os.path.dirname(os.path.abspath(__file__))
        DB_DIR: str = os.path.join(ABS_PATH,"db")

        loader=WebBaseLoader(url)
        data=loader.load()

        text_splitter = CharacterTextSplitter(separator='\n',
                                              chunk_size=1000,chunk_overlap=0)
        
        docs = text_splitter.split_documents(data)


        openai_embeddings = OpenAIEmbeddings()

        # client = chromadb.PersistentClient(path=DB_DIR)
        vectordb = FAISS.from_documents(documents=docs,embedding=openai_embeddings)


        # vectordb.persist()


        retriever=vectordb.as_retriever()

        llm=ChatOpenAI(model_name='gpt-3.5-turbo')

        qa=RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)


        response=qa(question)

        st.write(response)



st.title('Chat with Website')

url=st.text_input('Enter Your URL here:')

if url:
    assistant(url)