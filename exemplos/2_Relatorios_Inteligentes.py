import streamlit as st
import pandas as pd
import os
import re
import google.generativeai as genai
import json

# Configuração da página
st.set_page_config(
    page_title="Relatórios Inteligentes - Transcrições",
    page_icon="📑",
    layout="wide"
)

# Título da página
st.title("Relatórios Inteligentes")
st.markdown("### Gere relatórios automáticos das transcrições de reuniões usando IA")

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

# Função para ler arquivos Excel
def get_excel_data(file_path, sheet_name=None):
    """Carrega dados de um arquivo Excel.
    
    Args:
        file_path: Caminho para o arquivo Excel
        sheet_name: Nome da planilha específica para carregar. 
                    Se None, carrega todas as planilhas.
    
    Returns:
        Se sheet_name for None, retorna um dicionário com todas as planilhas.
        Se sheet_name for especificado, retorna um DataFrame com os dados da planilha.
    """
    if sheet_name is None:
        # Retorna um dicionário com todas as planilhas
        return pd.read_excel(file_path, sheet_name=None)
    else:
        # Retorna uma planilha específica
        return pd.read_excel(file_path, sheet_name=sheet_name)

# Função para configurar a API do Gemini
def configure_genai(api_key):
    genai.configure(api_key=api_key)

# Função para gerar relatório com Gemini
def generate_report(model, content, report_type):
    # Definir prompts baseados no tipo de relatório
    prompts = {
        "resumo": "Crie um resumo conciso da seguinte transcrição de reunião, destacando os principais pontos discutidos, decisões tomadas e próximos passos:",
        "resumo_expandido": "Crie um resumo detalhado da seguinte transcrição de reunião, incluindo todos os tópicos discutidos, decisões tomadas, responsabilidades atribuídas e prazos estabelecidos:",
        "insights": "Analise a seguinte transcrição de reunião e identifique insights importantes, padrões de comunicação, pontos de tensão, oportunidades de melhoria e recomendações:",
        "ata": "Crie uma ata formal da seguinte reunião, incluindo data, participantes, pauta, discussões, decisões e encaminhamentos:",
        "pontos_acao": "Extraia da seguinte transcrição de reunião todos os pontos de ação, tarefas atribuídas, responsáveis e prazos mencionados:"
    }
    
    # Estruturas de saída para cada tipo de relatório
    output_structures = {
        "resumo": {
            "resumo": "Resumo conciso da reunião",
            "principais_pontos": ["Ponto 1", "Ponto 2"],
            "decisoes": ["Decisão 1", "Decisão 2"],
            "proximos_passos": ["Passo 1", "Passo 2"]
        },
        "resumo_expandido": {
            "introducao": "Introdução sobre o contexto da reunião",
            "topicos_discutidos": [
                {"topico": "Tópico 1", "detalhes": "Detalhes da discussão"},
                {"topico": "Tópico 2", "detalhes": "Detalhes da discussão"}
            ],
            "decisoes": [
                {"decisao": "Decisão 1", "contexto": "Contexto da decisão"},
                {"decisao": "Decisão 2", "contexto": "Contexto da decisão"}
            ],
            "responsabilidades": [
                {"responsavel": "Nome", "tarefa": "Tarefa", "prazo": "Prazo"}
            ],
            "conclusao": "Conclusão da reunião"
        },
        "insights": {
            "insights_principais": [
                {"insight": "Insight 1", "explicacao": "Explicação detalhada"}
            ],
            "padroes_comunicacao": "Análise dos padrões de comunicação",
            "pontos_tensao": ["Ponto 1", "Ponto 2"],
            "oportunidades_melhoria": ["Oportunidade 1", "Oportunidade 2"],
            "recomendacoes": ["Recomendação 1", "Recomendação 2"]
        },
        "ata": {
            "cabecalho": {
                "titulo": "Título da reunião",
                "data": "Data da reunião",
                "horario": "Horário de início e término",
                "local": "Local ou plataforma",
                "participantes": ["Participante 1", "Participante 2"]
            },
            "pauta": ["Item 1", "Item 2"],
            "discussoes": [
                {"topico": "Tópico 1", "discussao": "Detalhes da discussão"}
            ],
            "decisoes": ["Decisão 1", "Decisão 2"],
            "encaminhamentos": [
                {"acao": "Ação", "responsavel": "Responsável", "prazo": "Prazo"}
            ],
            "proxima_reuniao": "Data e hora da próxima reunião"
        },
        "pontos_acao": {
            "acoes": [
                {
                    "acao": "Descrição da ação",
                    "responsavel": "Nome do responsável",
                    "prazo": "Prazo para conclusão",
                    "contexto": "Contexto em que a ação foi definida"
                }
            ],
            "pendencias": ["Pendência 1", "Pendência 2"],
            "observacoes": "Observações adicionais sobre os pontos de ação"
        }
    }
    
    # Selecionar prompt e estrutura de saída
    prompt = prompts.get(report_type, prompts["resumo"])
    output_structure = output_structures.get(report_type, output_structures["resumo"])
    
    # Construir o prompt completo
    full_prompt = f"{prompt}\n\nTranscrição:\n{content[:15000]}\n\nForneça a resposta em formato JSON estruturado conforme o exemplo a seguir:\n{json.dumps(output_structure, indent=2, ensure_ascii=False)}\n\nResponda APENAS com o JSON, sem texto adicional."
    
    try:
        # Gerar resposta com o modelo Gemini
        response = model.generate_content(full_prompt)
        
        # Extrair e processar a resposta JSON
        response_text = response.text
        
        # Tentar extrair JSON da resposta
        try:
            # Remover possíveis marcadores de código
            json_text = re.search(r'```json\n(.+?)\n```', response_text, re.DOTALL)
            if json_text:
                response_text = json_text.group(1)
            else:
                # Tentar encontrar apenas o conteúdo JSON
                json_text = re.search(r'\{.+\}', response_text, re.DOTALL)
                if json_text:
                    response_text = json_text.group(0)
            
            # Converter para objeto Python
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError as e:
            st.error(f"Erro ao processar a resposta JSON: {e}")
            st.text("Resposta recebida:")
            st.code(response_text)
            return None
    
    except Exception as e:
        st.error(f"Erro ao gerar relatório: {e}")
        return None

# Função para renderizar o relatório baseado no tipo
def render_report(report_data, report_type):
    if not report_data:
        st.error("Não foi possível gerar o relatório.")
        return
    
    if report_type == "resumo":
        st.subheader("Resumo da Reunião")
        st.write(report_data.get("resumo", ""))
        
        st.subheader("Principais Pontos")
        for ponto in report_data.get("principais_pontos", []):
            st.markdown(f"- {ponto}")
        
        st.subheader("Decisões Tomadas")
        for decisao in report_data.get("decisoes", []):
            st.markdown(f"- {decisao}")
        
        st.subheader("Próximos Passos")
        for passo in report_data.get("proximos_passos", []):
            st.markdown(f"- {passo}")
    
    elif report_type == "resumo_expandido":
        st.subheader("Introdução")
        st.write(report_data.get("introducao", ""))
        
        st.subheader("Tópicos Discutidos")
        for topico in report_data.get("topicos_discutidos", []):
            st.markdown(f"**{topico.get('topico', '')}**")
            st.write(topico.get("detalhes", ""))
        
        st.subheader("Decisões")
        for decisao in report_data.get("decisoes", []):
            st.markdown(f"**{decisao.get('decisao', '')}**")
            st.write(decisao.get("contexto", ""))
        
        st.subheader("Responsabilidades Atribuídas")
        # Criar dataframe para responsabilidades
        if report_data.get("responsabilidades"):
            resp_df = pd.DataFrame(report_data["responsabilidades"])
            st.table(resp_df)
        else:
            st.write("Nenhuma responsabilidade atribuída.")
        
        st.subheader("Conclusão")
        st.write(report_data.get("conclusao", ""))
    
    elif report_type == "insights":
        st.subheader("Insights Principais")
        for i, insight in enumerate(report_data.get("insights_principais", []), 1):
            with st.expander(f"Insight {i}: {insight.get('insight', '')}"):
                st.write(insight.get("explicacao", ""))
        
        st.subheader("Padrões de Comunicação")
        st.write(report_data.get("padroes_comunicacao", ""))
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Pontos de Tensão")
            for ponto in report_data.get("pontos_tensao", []):
                st.markdown(f"- {ponto}")
        
        with col2:
            st.subheader("Oportunidades de Melhoria")
            for oportunidade in report_data.get("oportunidades_melhoria", []):
                st.markdown(f"- {oportunidade}")
        
        st.subheader("Recomendações")
        for i, recomendacao in enumerate(report_data.get("recomendacoes", []), 1):
            st.markdown(f"**{i}.** {recomendacao}")
    
    elif report_type == "ata":
        # Cabeçalho
        cabecalho = report_data.get("cabecalho", {})
        st.subheader(cabecalho.get("titulo", "Ata de Reunião"))
        
        # Informações da reunião
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Data:** {cabecalho.get('data', '')}")
            st.markdown(f"**Horário:** {cabecalho.get('horario', '')}")
        with col2:
            st.markdown(f"**Local:** {cabecalho.get('local', '')}")
        
        # Participantes
        st.markdown("**Participantes:**")
        participantes = cabecalho.get("participantes", [])
        st.markdown(", ".join(participantes))
        
        # Pauta
        st.subheader("Pauta")
        for i, item in enumerate(report_data.get("pauta", []), 1):
            st.markdown(f"{i}. {item}")
        
        # Discussões
        st.subheader("Discussões")
        for discussao in report_data.get("discussoes", []):
            st.markdown(f"**{discussao.get('topico', '')}**")
            st.write(discussao.get("discussao", ""))
        
        # Decisões
        st.subheader("Decisões")
        for decisao in report_data.get("decisoes", []):
            st.markdown(f"- {decisao}")
        
        # Encaminhamentos
        st.subheader("Encaminhamentos")
        if report_data.get("encaminhamentos"):
            encam_df = pd.DataFrame(report_data["encaminhamentos"])
            st.table(encam_df)
        else:
            st.write("Nenhum encaminhamento registrado.")
        
        # Próxima reunião
        st.markdown(f"**Próxima reunião:** {report_data.get('proxima_reuniao', 'A definir')}")
    
    elif report_type == "pontos_acao":
        st.subheader("Pontos de Ação")
        
        # Criar dataframe para ações
        if report_data.get("acoes"):
            acoes_df = pd.DataFrame(report_data["acoes"])
            st.dataframe(acoes_df)
        else:
            st.write("Nenhum ponto de ação identificado.")
        
        st.subheader("Pendências")
        for pendencia in report_data.get("pendencias", []):
            st.markdown(f"- {pendencia}")
        
        if "observacoes" in report_data and report_data["observacoes"]:
            st.subheader("Observações")
            st.write(report_data["observacoes"])

# Interface principal

# Configuração da API Gemini usando secrets
try:
    # Tentar obter a chave da API do secrets.toml
    api_key = st.secrets["gemini"]["api_key"]
    configure_genai(api_key)
except Exception as e:
    # Fallback para entrada manual se não encontrar no secrets
    if 'gemini_api_key' not in st.session_state:
        st.session_state.gemini_api_key = ""
    
    with st.sidebar:
        api_key = st.text_input("Chave API do Google AI (Gemini)", 
                               value=st.session_state.gemini_api_key,
                               type="password",
                               label_visibility="collapsed")
        
        if api_key:
            st.session_state.gemini_api_key = api_key
            try:
                configure_genai(api_key)
            except Exception as e:
                pass

# Listar arquivos HTML e Excel
html_files = [f for f in os.listdir(output_dir) if f.endswith('.html')]
html_files.sort()

excel_files = [f for f in os.listdir(output_dir) if f.endswith('.xlsx')]
excel_files.sort()

# Seleção de arquivo
file_type = st.sidebar.radio("Selecione o tipo de arquivo", ["HTML (Transcrições)", "Excel (Dados)"])

if file_type == "HTML (Transcrições)":
    selected_file = st.sidebar.selectbox("Selecione uma transcrição", html_files)
    file_extension = "html"
else:  # Excel
    selected_file = st.sidebar.selectbox("Selecione um arquivo de dados", excel_files)
    file_extension = "xlsx"

# Seleção do tipo de relatório
report_types = {
    "resumo": "Resumo Conciso",
    "resumo_expandido": "Resumo Expandido",
    "insights": "Insights e Recomendações",
    "ata": "Ata Formal",
    "pontos_acao": "Pontos de Ação"
}

selected_report_type = st.sidebar.selectbox(
    "Selecione o tipo de relatório",
    list(report_types.keys()),
    format_func=lambda x: report_types[x]
)

# Botão para gerar relatório
generate_button = st.sidebar.button("Gerar Relatório", type="primary")

# Processar a geração do relatório
if selected_file and st.session_state.gemini_api_key and generate_button:
    file_path = os.path.join(output_dir, selected_file)
    
    # Extrair informações do nome do arquivo
    file_info = extract_info_from_filename(selected_file)
    if file_info:
        meeting_name = file_info["meeting_name"]
        st.subheader(f"Relatório: {meeting_name}")
    else:
        st.subheader(f"Relatório: {selected_file}")
    
    # Mostrar spinner durante o processamento
    with st.spinner("Gerando relatório... Isso pode levar alguns instantes."):
        try:
            # Carregar conteúdo do arquivo
            if file_extension == "html":
                content = get_html_content(file_path)
                # Extrair texto do HTML
                text_content = extract_text_from_html(content)
            else:  # Excel
                # Carregar todas as planilhas
                dfs = get_excel_data(file_path)
                # Combinar o conteúdo de todas as planilhas em texto
                text_parts = []
                for sheet_name, df in dfs.items():
                    text_parts.append(f"Planilha: {sheet_name}")
                    text_parts.append(df.to_string())
                text_content = "\n\n".join(text_parts)
            
            # Configurar modelo Gemini
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Gerar relatório
            report_data = generate_report(model, text_content, selected_report_type)
            
            # Renderizar relatório
            render_report(report_data, selected_report_type)
            
            # Opção para baixar o relatório como JSON
            if report_data:
                report_json = json.dumps(report_data, indent=2, ensure_ascii=False)
                st.download_button(
                    label="Baixar Relatório (JSON)",
                    data=report_json,
                    file_name=f"relatorio_{meeting_name}_{selected_report_type}.json",
                    mime="application/json"
                )
        
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")
            st.exception(e)

elif not st.session_state.gemini_api_key:
    st.info("Por favor, insira sua chave API do Google AI (Gemini) no menu lateral para gerar relatórios.")

elif not selected_file:
    st.info("Selecione um arquivo no menu lateral para começar.")

# Explicação dos tipos de relatório
with st.sidebar.expander("Sobre os Tipos de Relatório"):
    st.markdown("""
    - **Resumo Conciso**: Versão curta com os principais pontos da reunião.
    - **Resumo Expandido**: Versão detalhada com todos os tópicos e decisões.
    - **Insights e Recomendações**: Análise aprofundada com recomendações.
    - **Ata Formal**: Documento formal no formato de ata de reunião.
    - **Pontos de Ação**: Lista de tarefas, responsáveis e prazos definidos.
    """)

# Rodapé
st.sidebar.markdown("---")
st.sidebar.info("Esta página utiliza a API Gemini para gerar relatórios inteligentes a partir das transcrições de reuniões.")