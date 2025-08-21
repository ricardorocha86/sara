import streamlit as st 

# Configuração da página
st.set_page_config(
    page_title="Sara Carolayne - Entregáveis da Consultoria",
    page_icon="📋", 
    initial_sidebar_state="collapsed"
)

# Página inicial sempre disponível
paginas = {
    "Páginas": [st.Page("paginas/inicial.py", title="Início", icon='🏠', default=True),
                st.Page("paginas/visualizar_transcricoes.py", title="Visualizar Transcrições", icon='📄'),
                st.Page("paginas/analise_dados.py", title="Análise de Dados", icon='📊'),
                st.Page("paginas/relatorios.py", title="Relatórios IA", icon='📑'),
                st.Page("paginas/chat_documentos.py", title="Chat com Documentos", icon='💬')]
}
 

# Configura navegação
pg = st.navigation(paginas)
pg.run()
