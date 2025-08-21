import streamlit as st
import os
import zipfile
import io

# Configuração da página
st.set_page_config(
    page_title="Sara Carolayne - Entregáveis da Consultoria",
    page_icon="📋",
    layout="wide"
)

# Título da página
st.title("📋 Sara Carolayne - Entregáveis da Consultoria")
st.markdown("### Transcrições de Reuniões - Análise e Relatórios")

# Diretório de saída
output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "saidas")

# Função para criar ZIP das transcrições
def criar_zip_transcricoes():
    try:
        # Criar buffer de memória para o ZIP
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Adicionar todos os arquivos do diretório saidas
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, output_dir)
                    zip_file.write(file_path, arc_name)
        
        zip_buffer.seek(0)
        return zip_buffer, None
    except Exception as e:
        return None, str(e)

# Contar arquivos por tipo
def contar_arquivos():
    if os.path.exists(output_dir):
        files = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]
        excel_count = len([f for f in files if f.endswith('.xlsx')])
        html_count = len([f for f in files if f.endswith('.html')])
        return excel_count, html_count
    return 0, 0

# Funcionalidades em 4 colunas
st.markdown("---")
st.markdown("### 🎯 Funcionalidades Disponíveis")

col1, col2, col3, col4 = st.columns(4)

with col1:
    # Imagem para Visualizar Transcrições
    st.image("imagens/capa1.png", use_container_width=True)
    
    st.markdown("""
    **📄 Visualizar Transcrições**
    
    Acesse as transcrições completas das reuniões em formato HTML renderizado, com nomes destacados em azul para facilitar a leitura. 
    """)
    if st.button("📄 Acessar Transcrições", use_container_width=True, type="primary"):
        st.switch_page("paginas/visualizar_transcricoes.py")

with col2:
    # Imagem para Análise de Dados
    st.image("imagens/capa2.png", use_container_width=True)
    
    st.markdown("""
    **📊 Análise de Dados**
    
    Explore gráficos de participação, estatísticas de tempo de fala, velocidade da fala e evolução da participação ao longo das reuniões.
    """)
    if st.button("📊 Ver Análises", use_container_width=True, type="primary"):
        st.switch_page("paginas/analise_dados.py")

with col3:
    # Imagem para Relatórios Inteligentes
    st.image("imagens/capa3.png", use_container_width=True)
    
    st.markdown("""
    **📑 Relatórios Inteligentes**
    
    Gere automaticamente resumos, insights, atas formais e pontos de ação usando inteligência artificial.
    """)
    if st.button("📑 Gerar Relatórios", use_container_width=True, type="primary"):
        st.switch_page("paginas/relatorios.py")

with col4:
    # Imagem para Chat com Documentos
    st.image("imagens/capa4.png", use_container_width=True)
    
    st.markdown("""
    **💬 Chat com Documentos**
    
    Faça perguntas sobre todas as transcrições simultaneamente e obtenha respostas baseadas em IA sobre o conteúdo das reuniões.
    """)
    if st.button("💬 Fazer Perguntas", use_container_width=True, type="primary"):
        st.switch_page("paginas/chat_documentos.py")

# Download dos entregáveis
st.markdown("---")
st.markdown("### 📦 Download dos Entregáveis")

# Contar arquivos
excel_count, html_count = contar_arquivos()

# Informações do pacote
st.markdown(f"""
**📁 Pacote Completo**

O arquivo ZIP contém **{excel_count} arquivos Excel** e **{html_count} arquivos HTML** das transcrições das reuniões.
""")

# Botão de download
if os.path.exists(output_dir):
    files = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]
    if files:
        zip_buffer, error = criar_zip_transcricoes()
        if zip_buffer:
            st.download_button(
                label="⬇️ BAIXAR ARQUIVOS",
                data=zip_buffer.getvalue(),
                file_name="entregaveis_sara_carolayne.zip",
                mime="application/zip",
                use_container_width=True,
                type="primary"
            )
        else:
            st.error(f"Erro ao criar ZIP: {error}")
    else:
        st.info("📁 Nenhum arquivo encontrado")
else:
    st.info("📁 Diretório não encontrado")
 