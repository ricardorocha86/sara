import streamlit as st
import pandas as pd
import os
import re
import google.generativeai as genai

# Configuração da página
st.set_page_config(
    page_title="Converse com Documentos - Transcrições",
    page_icon="💬",
    layout="wide"
)

# Título da página
st.title("Converse com os Documentos")
st.markdown("### Faça perguntas sobre o conteúdo das transcrições de reuniões")
st.markdown("Utilize a caixa de texto abaixo para interagir com o conteúdo das suas transcrições. Você pode fazer perguntas específicas, pedir resumos ou buscar informações detalhadas. Por exemplo, tente perguntar: 'Qual foi o principal tópico da reunião de 09/08?', 'Quem participou da reunião de 16/08?', ou 'Resuma as decisões tomadas em todas as reuniões'.")

# Diretório de saída
output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "saidas")

# Função para extrair informações do nome do arquivo
def extract_info_from_filename(filename):
    # Padrão para extrair informações do nome do arquivo
    pattern = r"(html|excel)_(.+)\.(html|xlsx)"
    match = re.match(pattern, filename)
    if match:
        file_type = match.group(1)
        meeting_name = match.group(2)
        return {
            "type": file_type,
            "meeting_name": meeting_name
        }
    return None

# Função para ler arquivos HTML
def get_html_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Função para extrair texto limpo do HTML
def extract_text_from_html(html_content):
    # Remover tags HTML (implementação simplificada)
    # Em um cenário real, usaríamos BeautifulSoup ou similar
    text = re.sub(r'<.*?>', ' ', html_content)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# Função para configurar a API do Gemini
def configure_genai(api_key):
    genai.configure(api_key=api_key)

# Função para carregar e processar todos os documentos
@st.cache_data
def load_all_documents():
    documents = {}
    html_files = [f for f in os.listdir(output_dir) if f.endswith('.html')]
    
    for html_file in html_files:
        file_path = os.path.join(output_dir, html_file)
        file_info = extract_info_from_filename(html_file)
        
        if file_info:
            meeting_name = file_info["meeting_name"]
            html_content = get_html_content(file_path)
            text_content = extract_text_from_html(html_content)
            
            documents[meeting_name] = {
                "filename": html_file,
                "content": text_content,
                "path": file_path
            }
    
    return documents

# Função para responder perguntas com Gemini
def answer_question(model, question, context, meeting_name):
    # Construir o prompt
    prompt = f"""Você é um assistente especializado em analisar transcrições de reuniões. 
    Responda à pergunta com base apenas nas informações contidas na transcrição fornecida.
    Se a resposta não estiver na transcrição, diga claramente que não consegue responder com base nas informações disponíveis.
    
    Transcrição da reunião '{meeting_name}':
    {context[:15000]}
    
    Pergunta: {question}
    
    Resposta:"""
    
    try:
        # Gerar resposta com o modelo Gemini
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Erro ao gerar resposta: {e}")
        return f"Ocorreu um erro ao processar sua pergunta: {str(e)}"

# Função para responder perguntas com múltiplos documentos
def answer_with_multiple_documents(model, question, documents, selected_docs):
    # Construir contexto combinado
    combined_context = ""
    for doc_name in selected_docs:
        if doc_name in documents:
            doc_info = documents[doc_name]
            # Limitar o tamanho de cada documento para não exceder limites de tokens
            doc_content = doc_info["content"][:5000]  # Primeiros 5000 caracteres de cada documento
            combined_context += f"\n\nTranscrição da reunião '{doc_name}':\n{doc_content}\n"
    
    # Construir o prompt
    prompt = f"""Você é um assistente especializado em analisar transcrições de reuniões. 
    Responda à pergunta com base apenas nas informações contidas nas transcrições fornecidas.
    Se a resposta não estiver nas transcrições, diga claramente que não consegue responder com base nas informações disponíveis.
    Quando a informação estiver em uma transcrição específica, mencione qual reunião contém essa informação.
    
    Contexto das transcrições:
    {combined_context}
    
    Pergunta: {question}
    
    Resposta:"""
    
    try:
        # Gerar resposta com o modelo Gemini
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Erro ao gerar resposta: {e}")
        return f"Ocorreu um erro ao processar sua pergunta: {str(e)}"

# Interface principal

# Inicializar histórico de chat se não existir
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Inicializar chave API se não existir
if 'gemini_api_key' not in st.session_state:
    st.session_state.gemini_api_key = ""

# Configuração da API Gemini usando secrets
try:
    api_key = st.secrets["api_key"]
    configure_genai(api_key)
except Exception as e:
    st.error("Chave da API Gemini não encontrada. Por favor, configure-a no arquivo .streamlit/secrets.toml")
    st.stop()

# Carregar documentos
documents = load_all_documents()

# Sempre usar todos os documentos
selected_docs = list(documents.keys())

# Função para processar a pergunta
def process_question(question, selected_docs, documents):
    if question and selected_docs and st.session_state.gemini_api_key:
        # Mostrar spinner durante o processamento
        with st.spinner("Processando sua pergunta..."):
            try:
                # Configurar modelo Gemini
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # Gerar resposta
                if len(selected_docs) == 1:
                    # Resposta com um único documento
                    doc_name = selected_docs[0]
                    doc_info = documents[doc_name]
                    response = answer_question(model, question, doc_info["content"], doc_name)
                else:
                    # Resposta com múltiplos documentos
                    response = answer_with_multiple_documents(model, question, documents, selected_docs)
                
                # Adicionar resposta ao histórico
                st.session_state.chat_history.append({"role": "assistant", "content": response})
            
            except Exception as e:
                st.session_state.chat_history.append({"role": "assistant", "content": f"Erro: {str(e)}"})



user_question = st.chat_input(placeholder="Digite sua pergunta aqui...")
if user_question:
    st.session_state.chat_history.append({"role": "user", "content": user_question})
    process_question(user_question, selected_docs, documents)