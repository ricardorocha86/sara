import streamlit as st
import pandas as pd
import os
import re
import json

# Configuração da página
st.set_page_config(
    page_title="Relatórios Inteligentes - Transcrições",
    page_icon="📑",
    layout="wide"
)

# Título da página
st.title("📑 Relatórios Inteligentes")
st.markdown("### Geração automática de relatórios com inteligência artificial")

# Explicação dos tipos de relatório
st.markdown("""
**Tipos de relatórios disponíveis:**

- **📝 Resumo Conciso**: Versão curta com os principais pontos da reunião
- **📄 Resumo Expandido**: Versão detalhada com todos os tópicos e decisões  
- **💡 Insights**: Análise aprofundada com recomendações e padrões identificados
- **📋 Ata Formal**: Documento estruturado no formato oficial de ata de reunião
- **✅ Pontos de Ação**: Lista organizada de tarefas, responsáveis e prazos definidos
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

# Função para formatar nome do arquivo (remover html_)
def formatar_nome_arquivo(filename):
    if filename.startswith('html_'):
        return filename[5:]  # Remove "html_"
    return filename

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

# Função para gerar relatório com Gemini
def gerar_relatorio(model, content, report_type):
    # Definir prompts baseados no tipo de relatório
    prompts = {
        "resumo": "Crie um resumo conciso da seguinte transcrição de reunião, destacando os principais pontos discutidos, decisões tomadas e próximos passos. Responda diretamente com o conteúdo, sem introduções ou explicações:",
        "resumo_expandido": "Crie um resumo detalhado da seguinte transcrição de reunião, incluindo todos os tópicos discutidos, decisões tomadas, responsabilidades atribuídas e prazos estabelecidos. Responda diretamente com o conteúdo, sem introduções ou explicações:",
        "insights": "Analise a seguinte transcrição de reunião e identifique insights importantes, padrões de comunicação, pontos de tensão, oportunidades de melhoria e recomendações. Responda diretamente com o conteúdo, sem introduções ou explicações:",
        "ata": "Crie uma ata formal da seguinte reunião, incluindo data, participantes, pauta, discussões, decisões e encaminhamentos. Responda diretamente com o conteúdo, sem introduções ou explicações:",
        "pontos_acao": "Extraia da seguinte transcrição de reunião todos os pontos de ação, tarefas atribuídas, responsáveis e prazos mencionados. Responda diretamente com o conteúdo, sem introduções ou explicações:"
    }
    
    # Construir o prompt completo
    prompt = prompts.get(report_type, prompts["resumo"])
    full_prompt = f"{prompt}\n\nTranscrição:\n{content[:15000]}\n\nForneça uma resposta estruturada e detalhada em português, começando diretamente com o conteúdo solicitado."
    
    try:
        # Gerar resposta com o modelo Gemini
        response = model.generate_content(full_prompt)
        report_text = response.text
        
        # Remover linhas introdutórias comuns
        lines_to_remove = [
            "Aqui está um resumo detalhado da transcrição da reunião, estruturado conforme solicitado:",
            "Aqui está um resumo conciso da transcrição da reunião:",
            "Aqui está a análise da transcrição da reunião:",
            "Aqui está a ata formal da reunião:",
            "Aqui estão os pontos de ação extraídos da transcrição:",
            "Com base na transcrição fornecida, aqui está o resumo:",
            "Analisando a transcrição da reunião, identifiquei os seguintes pontos:",
            "Segue o resumo estruturado da reunião:",
            "Aqui está o relatório solicitado:",
            "Com base na transcrição, aqui estão os insights:",
            "Aqui está a ata estruturada:",
            "Segue a análise detalhada:",
            "Aqui estão os principais pontos identificados:",
            "Com base na transcrição da reunião:",
            "Aqui está o resumo estruturado:",
            "Segue o relatório solicitado:",
            "Aqui está a análise completa:",
            "Com base na transcrição fornecida:",
            "Aqui está o conteúdo estruturado:",
            "Segue a análise da reunião:"
        ]
        
        # Remover linhas introdutórias
        for line in lines_to_remove:
            report_text = report_text.replace(line, "").replace(line.replace(":", ""), "")
        
        # Limpar espaços extras e quebras de linha no início
        report_text = report_text.strip()
        
        return report_text
    except Exception as e:
        st.error(f"Erro ao gerar relatório: {e}")
        return None

# Função para criar HTML formatado
def criar_html_formatado(report_content, report_type, meeting_name):
    # Definir títulos baseados no tipo de relatório
    titles = {
        "resumo": "Resumo Conciso",
        "resumo_expandido": "Resumo Expandido",
        "insights": "Insights e Recomendações",
        "ata": "Ata Formal",
        "pontos_acao": "Pontos de Ação"
    }
    
    title = titles.get(report_type, "Relatório")
    
    # Usar biblioteca markdown para conversão automática
    try:
        import markdown
        # Configurar extensões para melhor conversão
        md = markdown.Markdown(extensions=['extra', 'nl2br'])
        html_content = md.convert(report_content)
    except ImportError:
        # Fallback simples se markdown não estiver disponível
        html_content = f'<div style="white-space: pre-wrap;">{report_content}</div>'
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title} - {meeting_name}</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #2c3e50;
                background-color: #f8f9fa;
                padding: 20px;
            }}
            
            .container {{
                max-width: 800px;
                margin: 0 auto;
                background-color: white;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px 30px;
                text-align: center;
            }}
            
            .header h1 {{
                font-size: 2.5em;
                font-weight: 300;
                margin-bottom: 10px;
                letter-spacing: 1px;
            }}
            
            .header .meta {{
                font-size: 1.1em;
                opacity: 0.9;
                margin-top: 15px;
            }}
            
            .content {{
                padding: 40px 30px;
                font-size: 1.1em;
                line-height: 1.8;
            }}
            
            h2 {{
                color: #34495e;
                font-size: 1.8em;
                margin: 30px 0 20px 0;
                padding-bottom: 10px;
                border-bottom: 3px solid #3498db;
                font-weight: 600;
            }}
            
            h3 {{
                color: #2980b9;
                font-size: 1.4em;
                margin: 25px 0 15px 0;
                font-weight: 600;
            }}
            
            h4 {{
                color: #2980b9;
                font-size: 1.2em;
                margin: 20px 0 10px 0;
                font-weight: 600;
            }}
            
            p {{
                margin-bottom: 20px;
                text-align: justify;
                color: #2c3e50;
            }}
            
            ul, ol {{
                margin: 20px 0;
                padding-left: 30px;
            }}
            
            li {{
                margin-bottom: 12px;
                line-height: 1.7;
                color: #2c3e50;
            }}
            
            strong {{
                color: #2c3e50;
                font-weight: 700;
                background-color: #f8f9fa;
                padding: 2px 6px;
                border-radius: 4px;
            }}
            
            em {{
                color: #7f8c8d;
                font-style: italic;
                font-weight: 500;
            }}
            
            .footer {{
                background-color: #ecf0f1;
                padding: 30px;
                text-align: center;
                border-top: 1px solid #ddd;
            }}
            
            .footer p {{
                margin: 5px 0;
                color: #7f8c8d;
                font-size: 0.95em;
            }}
            
            .highlight {{
                background-color: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 20px;
                margin: 20px 0;
                border-radius: 4px;
            }}
            
            @media print {{
                body {{
                    background-color: white;
                    padding: 0;
                }}
                .container {{
                    box-shadow: none;
                    border-radius: 0;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{title}</h1>
                <div class="meta">
                    <div><strong>Reunião:</strong> {meeting_name}</div>
                    <div><strong>Data de geração:</strong> {pd.Timestamp.now().strftime('%d/%m/%Y às %H:%M')}</div>
                </div>
            </div>
            
            <div class="content">
                {html_content}
            </div>
            
            <div class="footer">
                <p><strong>Relatório gerado automaticamente</strong></p>
                <p>Sistema de Análise de Transcrições</p>
                <p>Sara Carolayne - Entregáveis da Consultoria</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_template

# Interface principal

# Configuração da API Gemini usando secrets
try:
    # Tentar obter a chave da API do secrets.toml
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

# Listar arquivos HTML
html_files = [f for f in os.listdir(output_dir) if f.endswith('.html')]
html_files.sort()

# Gerador de Relatórios Rápidos
st.markdown("---")
st.markdown("### 🚀 Gerador de Relatórios Rápidos")

# Layout com 6 colunas
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    # Seletor de transcrição
    selected_file = st.selectbox(
        "Selecione a transcrição:",
        html_files,
        format_func=formatar_nome_arquivo,
        label_visibility="collapsed"
    )

# Variáveis para armazenar o relatório gerado
if 'current_report' not in st.session_state:
    st.session_state.current_report = None
if 'current_report_type' not in st.session_state:
    st.session_state.current_report_type = None
if 'current_meeting_name' not in st.session_state:
    st.session_state.current_meeting_name = None

with col2:
    # Botão Resumo Conciso
    if st.button("📝 Resumo Conciso", use_container_width=True, type="primary"):
        if selected_file and genai:
            with st.spinner("Gerando resumo conciso...", show_time=True):
                file_path = os.path.join(output_dir, selected_file)
                content = ler_html(file_path)
                text_content = extrair_texto_html(content)
                model = genai.GenerativeModel('gemini-2.5-flash')
                report = gerar_relatorio(model, text_content, "resumo")
                
                if report:
                    file_info = extrair_info_arquivo(selected_file)
                    meeting_name = file_info["meeting_name"] if file_info else selected_file
                    
                    st.session_state.current_report = report
                    st.session_state.current_report_type = "resumo"
                    st.session_state.current_meeting_name = meeting_name
                    st.rerun()

with col3:
    # Botão Resumo Expandido
    if st.button("📄 Resumo Expandido", use_container_width=True, type="primary"):
        if selected_file and genai:
            with st.spinner("Gerando resumo expandido...", show_time=True):
                file_path = os.path.join(output_dir, selected_file)
                content = ler_html(file_path)
                text_content = extrair_texto_html(content)
                model = genai.GenerativeModel('gemini-2.5-flash')
                report = gerar_relatorio(model, text_content, "resumo_expandido")
                
                if report:
                    file_info = extrair_info_arquivo(selected_file)
                    meeting_name = file_info["meeting_name"] if file_info else selected_file
                    
                    st.session_state.current_report = report
                    st.session_state.current_report_type = "resumo_expandido"
                    st.session_state.current_meeting_name = meeting_name
                    st.rerun()

with col4:
    # Botão Insights
    if st.button("💡 Insights", use_container_width=True, type="primary"):
        if selected_file and genai:
            with st.spinner("Gerando insights...", show_time=True):
                file_path = os.path.join(output_dir, selected_file)
                content = ler_html(file_path)
                text_content = extrair_texto_html(content)
                model = genai.GenerativeModel('gemini-2.5-flash')
                report = gerar_relatorio(model, text_content, "insights")
                
                if report:
                    file_info = extrair_info_arquivo(selected_file)
                    meeting_name = file_info["meeting_name"] if file_info else selected_file
                    
                    st.session_state.current_report = report
                    st.session_state.current_report_type = "insights"
                    st.session_state.current_meeting_name = meeting_name
                    st.rerun()

with col5:
    # Botão Ata Formal
    if st.button("📋 Ata Formal", use_container_width=True, type="primary"):
        if selected_file and genai:
            with st.spinner("Gerando ata formal...", show_time=True):
                file_path = os.path.join(output_dir, selected_file)
                content = ler_html(file_path)
                text_content = extrair_texto_html(content)
                model = genai.GenerativeModel('gemini-2.5-flash')
                report = gerar_relatorio(model, text_content, "ata")
                
                if report:
                    file_info = extrair_info_arquivo(selected_file)
                    meeting_name = file_info["meeting_name"] if file_info else selected_file
                    
                    st.session_state.current_report = report
                    st.session_state.current_report_type = "ata"
                    st.session_state.current_meeting_name = meeting_name
                    st.rerun()

with col6:
    # Botão Pontos de Ação
    if st.button("✅ Pontos de Ação", use_container_width=True, type="primary"):
        if selected_file and genai:
            with st.spinner("Extraindo pontos de ação...", show_time=True):
                file_path = os.path.join(output_dir, selected_file)
                content = ler_html(file_path)
                text_content = extrair_texto_html(content)
                model = genai.GenerativeModel('gemini-2.5-flash')
                report = gerar_relatorio(model, text_content, "pontos_acao")
                
                if report:
                    file_info = extrair_info_arquivo(selected_file)
                    meeting_name = file_info["meeting_name"] if file_info else selected_file
                    
                    st.session_state.current_report = report
                    st.session_state.current_report_type = "pontos_acao"
                    st.session_state.current_meeting_name = meeting_name
                    st.rerun()

# Exibir relatório fora das colunas
if st.session_state.current_report:
    st.markdown("---")
    
    # Definir títulos baseados no tipo de relatório
    titles = {
        "resumo": "📝 Resumo Conciso",
        "resumo_expandido": "📄 Resumo Expandido",
        "insights": "💡 Insights e Recomendações",
        "ata": "📋 Ata Formal",
        "pontos_acao": "✅ Pontos de Ação"
    }
    
    title = titles.get(st.session_state.current_report_type, "Relatório")
    st.markdown(f"## {title}")
    st.markdown(f"**Reunião:** {st.session_state.current_meeting_name}")
    
    # Exibir o relatório
    st.markdown(st.session_state.current_report)
    
    # Botão de download em HTML
    html_content = criar_html_formatado(
        st.session_state.current_report, 
        st.session_state.current_report_type, 
        st.session_state.current_meeting_name
    )
    
    st.download_button(
        label="⬇️ Baixar Relatório (HTML)",
        data=html_content,
        file_name=f"{st.session_state.current_report_type}_{st.session_state.current_meeting_name}.html",
        mime="text/html",
        use_container_width=True
    )

elif not genai:
    st.info("Por favor, insira sua chave API do Google AI (Gemini) para gerar relatórios.")

elif not selected_file:
    st.info("Selecione uma transcrição para começar.")
