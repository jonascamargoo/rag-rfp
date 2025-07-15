import json
import os
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import streamlit as st

from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.embeddings import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from cookie_utils import get_formatted_cookies



load_dotenv()

def extract_content_from_json(soup: BeautifulSoup) -> str:
    script_tag = soup.find('script', id='__NEXT_DATA__')
    if not script_tag:
        print("--> AVISO: Tag de script não encontrada.")
        return "Conteúdo JSON não encontrado"

    try:
        data = json.loads(script_tag.string)
        article_blocks = data['props']['pageProps']['articleContent']['blocks']
        
        content_parts = []
        for block in article_blocks:
            if block.get('text'):
                content_parts.append(block['text'])

        full_content = "\n\n".join(content_parts).strip()
        return full_content if full_content else "Conteúdo vazio nos blocos JSON"
        
    except (KeyError, TypeError) as e:
        print(f"--> ERRO ao extrair JSON: Chave não encontrada ou estrutura inesperada - {e}")
        return "Falha ao analisar a estrutura do JSON"
    
    
def load_docs(urls: list[str], cookies: list) -> list[Document]:
    all_docs = []
    print("Iniciando o Playwright para coleta de dados...")
    with sync_playwright() as p:
        # headless=False para ver o navegador abrindo - debugging
        # headless=True para rodar em segundo plano
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        try:
            context.add_cookies(cookies)
            print("-> Cookies carregados com sucesso do ambiente.")
        except Exception as e:
            print(f"--> ERRO AO CARREGAR COOKIES: {e}")
            browser.close()
            return []

        page = context.new_page()

        for url in urls:
            print(f"\n--- Coletando de: {url} ---")
            try:
                page.goto(url, wait_until='domcontentloaded') 
                html_content = page.content()
                soup = BeautifulSoup(html_content, 'html.parser')
                
                title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "Título não encontrado"
                
                content = extract_content_from_json(soup)
                
                print(f"TÍTULO EXTRAÍDO: {title}")
                print(f"CONTEÚDO EXTRAÍDO (PRIMEIROS 150 CARACTERES): {content[:150]}...")

                if "Conteúdo não encontrado" in content or "Falha ao analisar" in content:
                     print(f"AVISO: Não foi possível extrair o conteúdo de {url}.")

                doc = Document(
                    page_content=f"TITLE: {title}\n\nCONTENT:\n{content}",
                    metadata={"source": url}
                )
                all_docs.append(doc)
                
            except Exception as e:
                print(f"--> ERRO ao processar a URL {url}: {e}")
        
        browser.close()
        print("\nPlaywright finalizado.")
    return all_docs




@st.cache_resource
def create_rag_chain():
    urls_string = os.getenv("ARTICLE_URLS")
    
    
    article_urls = urls_string.split(',')
    session_cookies = get_formatted_cookies()

    
    docs = load_docs(article_urls, session_cookies)
    
    if not docs:
        raise ValueError("Nenhum documento foi carregado. Verifique a extração de conteúdo e os cookies.")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    
    # embedding_model = OllamaEmbeddings(model="mxbai-embed-large")
    embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

    vectorstore = Chroma.from_documents(documents=splits, embedding=embedding_model)
    retriever = vectorstore.as_retriever()
    
    # llm = ChatOllama(model="llama3", temperature=0)
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    

    template = """Based solely on the CONTEXT from the provided knowledge base, answer whether the company meets the following DEMAND or not.
    Add a comment justifying your answer based on the context.
    Your answer must be one of the three options: 'YES', 'NO', or 'PARTIALLY'.

    CONTEXT:
    {context}

    DEMAND:
    {question}

    ANSWER (YES/NO/PARTIALLY) and COMMENT:
    """
    prompt = ChatPromptTemplate.from_template(template)

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain
