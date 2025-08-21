import streamlit as st
import os
import re

# Configuração da página
st.set_page_config(
    page_title="Visualizar Transcrições - Sara Carolayne",
    page_icon="📄",
    layout="wide"
)

# Título da página
st.title("📄 Visualizar Transcrições")
st.markdown("### Acesse as transcrições completas das reuniões")

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

# Função para destacar nomes em azul escuro e negrito
def destacar_nomes(html_content):
    # Padrão para encontrar nomes (assumindo que estão em tags como <strong>, <b>, ou seguidos de ":")
    # Primeiro, vamos destacar nomes que estão em tags existentes
    html_content = re.sub(r'<strong>([^<]+)</strong>', r'<strong style="color: #1f4e79; font-weight: bold;">\1</strong>', html_content)
    html_content = re.sub(r'<b>([^<]+)</b>', r'<b style="color: #1f4e79; font-weight: bold;">\1</b>', html_content)
    
    # Para nomes que não estão em tags, vamos procurar por padrões como "Nome:"
    # Esta é uma abordagem mais conservadora para não quebrar o HTML
    return html_content

# Listar arquivos HTML
html_files = [f for f in os.listdir(output_dir) if f.endswith('.html')]
html_files.sort()

if not html_files:
    st.warning("📁 Nenhum arquivo HTML encontrado no diretório 'saidas'")
else:
    # Duas colunas no início
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Seleção de arquivo
        selected_file = st.selectbox(
            "Selecione uma transcrição:",
            html_files,
            format_func=lambda x: extrair_info_arquivo(x)["meeting_name"] if extrair_info_arquivo(x) else x,
            label_visibility="collapsed"
        )
    
    with col2:
        if selected_file:
            file_path = os.path.join(output_dir, selected_file)
            
            # Botão para baixar o arquivo
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
                
            st.download_button(
                label="⬇️ Baixar",
                data=file_content,
                file_name=selected_file,
                mime="text/html",
                use_container_width=True
            )
    
    if selected_file:
        file_path = os.path.join(output_dir, selected_file)
        
        # Extrair informações do nome do arquivo
        file_info = extrair_info_arquivo(selected_file)
        if file_info:
            meeting_name = file_info["meeting_name"]
            st.subheader(f"📋 {meeting_name}")
        else:
            st.subheader(f"📋 {selected_file}") 
        
        # Ler e processar o conteúdo
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
        
        # Destacar nomes em azul escuro e negrito
        processed_content = destacar_nomes(file_content)
        
        # Sempre mostrar HTML renderizado
        st.components.v1.html(processed_content, height=600, scrolling=True)

# Lista de arquivos disponíveis
st.sidebar.markdown("### 📁 Transcrições Disponíveis")

if html_files:
    for file in html_files:
        file_info = extrair_info_arquivo(file)
        if file_info:
            st.sidebar.markdown(f"• **{file_info['meeting_name']}**")
        else:
            st.sidebar.markdown(f"• {file}")
else:
    st.sidebar.warning("Nenhum arquivo encontrado")
