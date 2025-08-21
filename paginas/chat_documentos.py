import streamlit as st
import pandas as pd
import os
import re

# Configuração da página
st.set_page_config(
    page_title="Converse com Documentos - Transcrições",
    page_icon="💬",
    layout="wide"
)

# Título da página
st.title("💬 Chat com Documentos")
st.markdown("### Faça perguntas sobre as reuniões")

# Explicação e exemplos de perguntas
st.markdown("""
**Esta seção permite que você faça perguntas sobre todas as transcrições das reuniões. O sistema analisa todo o conteúdo disponível para fornecer respostas precisas.**

**💡 Exemplos de perguntas:**
- Quais decisões foram tomadas em todas as reuniões?
- Quais são os temas mais recorrentes?
- Compare as reuniões de agosto e setembro
- Identifique padrões de participação
- Faça um resumo sobre as participações de Sara Carolayne
""")

# Diretório de saída
output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "saidas")

# Função para extrair informações do nome do arquivo
def extrair_info_arquivo(filename):
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
def ler_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Função para extrair texto limpo do HTML
def extrair_texto_html(html_content):
    # Remover tags HTML (implementação simplificada)
    text = re.sub(r'<.*?>', ' ', html_content)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# Função para configurar a API do Gemini
def configurar_genai(api_key):
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        return genai
    except ImportError:
        st.error("Biblioteca google-generativeai não instalada. Execute: pip install google-generativeai")
        return None

# Função para carregar e processar todos os documentos
@st.cache_data
def carregar_documentos():
    documents = {}
    html_files = [f for f in os.listdir(output_dir) if f.endswith('.html')]
    
    for html_file in html_files:
        file_path = os.path.join(output_dir, html_file)
        file_info = extrair_info_arquivo(html_file)
        
        if file_info:
            meeting_name = file_info["meeting_name"]
            html_content = ler_html(file_path)
            text_content = extrair_texto_html(html_content)
            
            documents[meeting_name] = {
                "filename": html_file,
                "content": text_content,
                "path": file_path
            }
    
    return documents

# Função para responder perguntas com múltiplos documentos
def responder_multiplos_documentos(model, question, documents):
    # Construir contexto combinado de todos os documentos
    combined_context = ""
    for doc_name, doc_info in documents.items():
        # Limitar o tamanho de cada documento para não exceder limites de tokens
        doc_content = doc_info["content"] 
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

# Configuração da API Gemini usando secrets
try:
    api_key = st.secrets["gemini"]["api_key"]
    genai = configurar_genai(api_key)
except Exception as e:
    # Fallback para entrada manual se não encontrar no secrets
    if 'gemini_api_key' not in st.session_state:
        st.session_state.gemini_api_key = ""
    
    api_key = st.text_input("Chave API do Google AI (Gemini)", 
                           value=st.session_state.gemini_api_key,
                           type="password",
                           label_visibility="collapsed")
    
    if api_key:
        st.session_state.gemini_api_key = api_key
        genai = configurar_genai(api_key)
    else:
        genai = None

# Carregar documentos
documents = carregar_documentos()

# Interface de chat simplificada
st.markdown("---")
st.markdown("### 💬 Faça sua pergunta")

# Campo de entrada para pergunta
user_question = st.text_area(
    "Digite sua pergunta:",
    placeholder="Ex: Faça um resumo sobre as participações de Sara Carolayne",
    height=150,
    label_visibility="collapsed"
)

# Botão para processar pergunta
if st.button("🔍 Buscar Resposta", type="primary", use_container_width=True):
    if user_question and genai and documents:
        with st.spinner("Processando sua pergunta...", show_time=True):
            try:
                # Configurar modelo Gemini
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # Gerar resposta usando todos os documentos
                response = responder_multiplos_documentos(model, user_question, documents)
                
                # Exibir resposta
                st.markdown("---")
                st.markdown("### 📋 Resposta")
                st.markdown(response)
                
            except Exception as e:
                st.error(f"Erro ao processar pergunta: {str(e)}")
    elif not user_question:
        st.warning("Por favor, digite uma pergunta.")
    elif not genai:
        st.error("Chave API do Gemini não configurada.")
    elif not documents:
        st.error("Nenhum documento encontrado no diretório 'saidas'.")
