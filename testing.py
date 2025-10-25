import os
import google.generativeai as genai
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI

os.environ['GOOGLE_API_KEY'] = 'AIzaSyDpXnQhfq6lKfrXK5n4ka2WBUDZFa8ilco'
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

# Create a sample text file
text_content = """ 
Machine learning is a subset of artificial intelligence (AI) that enables systems to learn from data and make decisions without explicit programming. It can be categorized into three main types:
"""

with open("machine_learning.txt", "w") as file:
    file.write(text_content)
print('Sample file created successfully!')

# Load the document
loader = TextLoader("machine_learning.txt")
documents = loader.load()

# Split the text into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = text_splitter.split_documents(documents)

# Convert text into embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(docs, embeddings)

# Initialize the LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")

# Setup Retrieval QA
qa = RetrievalQA.from_chain_type(llm, chain_type="stuff", retriever=vectorstore.as_retriever())

print("\nGemini RAG chatbot! Ask a question about Machine Learning.")

# Chatbot loop
while True:
    query = input('\nAsk a question and type exit to quit: ')
    if query.lower() == 'exit':
        print('Goodbye!')
        break
    answer = qa.invoke({"query": query})  
    print(f'\nAI: {answer}')