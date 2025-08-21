import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
import re

# Configuração da página
st.set_page_config(
    page_title="Análise de Dados - Transcrições",
    page_icon="📊",
    layout="wide"
)

# Título da página
st.title("📊 Análise de Dados")
st.markdown("### Estatísticas das reuniões")

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

# Função para formatar nome do arquivo (remover excel_)
def formatar_nome_arquivo(filename):
    if filename.startswith('excel_'):
        return filename[6:]  # Remove "excel_"
    return filename

# Função para ler arquivos Excel
def carregar_excel(file_path):
    return pd.read_excel(file_path, sheet_name=None)

# Listar arquivos Excel
excel_files = [f for f in os.listdir(output_dir) if f.endswith('.xlsx')]
excel_files.sort()

# Layout principal com seletor e métricas
col1, col2 = st.columns([3, 1])

with col1:
    # Seletor de arquivo
    st.markdown("### 📁 Selecionar Arquivo")
    selected_excel = st.selectbox(
        "Escolha o arquivo para análise:",
        excel_files,
        format_func=formatar_nome_arquivo,
        label_visibility="collapsed"
    )

with col2:
    # Seletor de arquivo
    st.markdown(" ")
 

if selected_excel:
    file_path = os.path.join(output_dir, selected_excel)
    
    # Extrair informações do nome do arquivo
    file_info = extrair_info_arquivo(selected_excel)
    if file_info:
        meeting_name = file_info["meeting_name"]
        st.markdown("---")
        st.markdown(f"## 📋 Análise de: **{meeting_name}**")
    else:
        st.markdown("---")
        st.markdown(f"## 📋 Análise de: **{selected_excel}**")
    
    # Carregar dados do Excel
    try:
        dfs = carregar_excel(file_path)
        first_sheet = list(dfs.keys())[0]
        df = dfs[first_sheet]
        
        # Verificar se o dataframe tem as colunas esperadas (formato real)
        expected_columns = ['locutor', 'inicio', 'fim', 'duracao', 'palavras']
        has_expected_columns = all(col in df.columns for col in expected_columns)
        
        if has_expected_columns:
            # Métricas principais em cards
            st.markdown("### 📈 Métricas Principais")
            
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            
            with metric_col1:
                total_speakers = df['locutor'].nunique()
                st.metric("👥 Participantes", total_speakers)
            
            with metric_col2:
                total_utterances = len(df)
                st.metric("💬 Falas", total_utterances)
            
            with metric_col3:
                if 'duracao' in df.columns:
                    total_duration = df['duracao'].sum() / 60
                    st.metric("⏱️ Duração Total", f"{total_duration:.1f} min")
                else:
                    st.metric("⏱️ Duração", "N/A")
            
            with metric_col4:
                if 'palavras' in df.columns:
                    total_words = df['palavras'].sum()
                    st.metric("📝 Total Palavras", f"{total_words:,}")
                else:
                    st.metric("📝 Palavras", "N/A")
            
            st.markdown("---")
            
            # Dashboard com gráficos em colunas
            st.markdown("## 📊 Análises Detalhadas")
            
            # Primeira linha: Participação e Tempo de Fala
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 👥 Participação por Pessoa")
                st.markdown("*Identifica quem mais contribuiu na reunião e quem pode precisar de mais espaço para falar.*")
                
                speaker_counts = df['locutor'].value_counts().reset_index()
                speaker_counts.columns = ['Participante', 'Falas']
                
                fig = px.bar(speaker_counts, x='Participante', y='Falas',
                           color_discrete_sequence=['#1f77b4'],
                           title="Número de Falas por Participante")
                fig.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### ⏱️ Distribuição do Tempo de Fala")
                st.markdown("*Mostra se o tempo foi distribuído de forma equilibrada entre os participantes.*")
                
                if 'duracao' in df.columns:
                    speaker_duration = df.groupby('locutor')['duracao'].sum().reset_index()
                    speaker_duration.columns = ['Participante', 'Duração (segundos)']
                    speaker_duration['Duração (minutos)'] = speaker_duration['Duração (segundos)'] / 60
                    
                    total_duration = speaker_duration['Duração (segundos)'].sum()
                    speaker_duration['Percentual'] = (speaker_duration['Duração (segundos)'] / total_duration * 100).round(1)
                    
                    fig = px.pie(speaker_duration, values='Percentual', names='Participante',
                               title="Percentual do Tempo de Fala",
                               hover_data=['Duração (minutos)'])
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
            # Segunda linha: Velocidade da Fala e Evolução da Reunião
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🗣️ Velocidade da Fala")
                st.markdown("*Ajuda a identificar se algum participante fala muito rápido ou lento, afetando a compreensão.*")
                
                if 'palavras' in df.columns and 'duracao' in df.columns:
                    df['wpm'] = (df['palavras'] / df['duracao']) * 60
                    df['wpm'] = df['wpm'].fillna(0).clip(0, 500)
                    
                    wpm_by_speaker = df.groupby('locutor')['wpm'].mean().reset_index()
                    wpm_by_speaker.columns = ['Participante', 'WPM Médio']
                    wpm_by_speaker = wpm_by_speaker.sort_values('WPM Médio', ascending=False)
                    
                    fig = px.bar(wpm_by_speaker, x='Participante', y='WPM Médio',
                               color_discrete_sequence=['#ff7f0e'],
                               title="Velocidade Média da Fala (Palavras por Minuto)")
                    fig.update_layout(showlegend=False, height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### 📈 Evolução da Participação ao Longo da Reunião")
                st.markdown("*Mostra se a participação foi consistente ou se houve momentos de maior ou menor engajamento.*")
                
                if 'inicio' in df.columns and len(df) > 0:
                    try:
                        df_sorted = df.sort_values('inicio')
                        max_time = df_sorted['inicio'].max()
                        
                        df_sorted['fase'] = 'Meio'
                        df_sorted.loc[df_sorted['inicio'] <= max_time * 0.33, 'fase'] = 'Início'
                        df_sorted.loc[df_sorted['inicio'] >= max_time * 0.67, 'fase'] = 'Fim'
                        
                        participation_by_phase = df_sorted.groupby(['fase', 'locutor']).size().unstack(fill_value=0)
                        
                        # Usar degradê de azuis (6 tons)
                        azuis_degrade = ['#e3f2fd', '#bbdefb', '#90caf9', '#64b5f6', '#42a5f5', '#2196f3']
                        
                        fig = px.bar(participation_by_phase, 
                                   title="Participação por Fase da Reunião",
                                   labels={'value': 'Falas', 'fase': 'Fase da Reunião'},
                                   color_discrete_sequence=azuis_degrade)
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                        
                    except Exception as e:
                        st.info("Não foi possível analisar a evolução temporal dos dados.")
            
            # Resumo estatístico
            st.markdown("---")
            st.markdown("### 📋 Resumo Estatístico por Participante")
            st.markdown("*Visão consolidada das métricas principais para cada participante.*")
            
            summary_stats = df.groupby('locutor').agg({
                'locutor': 'count',
                'palavras': ['sum', 'mean'] if 'palavras' in df.columns else ['count', 'count'],
                'duracao': ['sum', 'mean'] if 'duracao' in df.columns else ['count', 'count']
            }).round(1)
            
            if 'palavras' in df.columns and 'duracao' in df.columns:
                summary_stats.columns = ['Falas', 'Total Palavras', 'Média Palavras', 'Total Duração (s)', 'Média Duração (s)']
            else:
                summary_stats.columns = ['Falas', 'Col1', 'Col2', 'Col3', 'Col4']
            
            summary_stats = summary_stats.sort_values('Falas', ascending=False)
            
            st.dataframe(summary_stats, use_container_width=True)
        
        else:
            st.warning("O formato do arquivo não corresponde ao esperado. Verifique se contém as colunas: 'locutor', 'inicio', 'fim', 'duracao', 'palavras'.")
            st.info(f"Colunas disponíveis: {', '.join(df.columns)}")
    
    except Exception as e:
        st.error(f"Erro ao carregar ou analisar o arquivo: {e}")

else:
    st.info("Selecione um arquivo para começar a análise.")
