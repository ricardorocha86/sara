import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Configuração da página
st.set_page_config(
    page_title="Análise de Dados - Transcrições",
    page_icon="📊",
    layout="wide"
)

# Título da página
st.title("Análise de Dados das Transcrições")
st.markdown("### Visualize insights e estatísticas das transcrições de reuniões")

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

# Função para baixar NLTK stopwords se necessário
@st.cache_resource
def download_nltk_resources():
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')

# Baixar recursos NLTK
download_nltk_resources()

# Função para processar texto e remover stopwords
def process_text(text, language='portuguese'):
    # Tokenizar o texto
    tokens = word_tokenize(text.lower(), language=language)
    
    # Remover stopwords
    stop_words = set(stopwords.words(language))
    filtered_tokens = [word for word in tokens if word.isalpha() and word not in stop_words]
    
    return filtered_tokens

# Função para criar nuvem de palavras
def create_wordcloud(text, title="Nuvem de Palavras"):
    from wordcloud import WordCloud
    
    # Criar nuvem de palavras
    wordcloud = WordCloud(width=800, height=400, background_color='white', 
                         colormap='viridis', max_words=100).generate(text)
    
    # Plotar a nuvem de palavras
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.set_title(title, fontsize=15)
    ax.axis('off')
    
    return fig

# Função para analisar sentimentos (simplificada)
def analyze_sentiment(text):
    # Esta é uma análise de sentimento muito simplificada
    # Em um cenário real, usaríamos uma biblioteca como TextBlob, VADER ou um modelo de ML
    
    # Lista de palavras positivas e negativas em português
    positive_words = ['bom', 'ótimo', 'excelente', 'positivo', 'feliz', 'concordo', 'aprovado', 
                     'sucesso', 'eficiente', 'eficaz', 'melhor', 'progresso', 'avanço']
    
    negative_words = ['ruim', 'péssimo', 'negativo', 'triste', 'discordo', 'reprovado', 
                     'fracasso', 'ineficiente', 'ineficaz', 'pior', 'problema', 'dificuldade']
    
    # Tokenizar o texto
    tokens = word_tokenize(text.lower(), language='portuguese')
    
    # Contar palavras positivas e negativas
    positive_count = sum(1 for word in tokens if word in positive_words)
    negative_count = sum(1 for word in tokens if word in negative_words)
    
    # Calcular pontuação de sentimento
    total = positive_count + negative_count
    if total == 0:
        return 0  # Neutro
    
    sentiment_score = (positive_count - negative_count) / total
    return sentiment_score

# Listar arquivos Excel
excel_files = [f for f in os.listdir(output_dir) if f.endswith('.xlsx')]
excel_files.sort()

# Sidebar para seleção de arquivo
selected_excel = st.sidebar.selectbox("Selecione um arquivo para análise", excel_files)

if selected_excel:
    file_path = os.path.join(output_dir, selected_excel)
    
    # Extrair informações do nome do arquivo
    file_info = extract_info_from_filename(selected_excel)
    if file_info:
        meeting_name = file_info["meeting_name"]
        st.subheader(f"Análise de: {meeting_name}")
    else:
        st.subheader(f"Análise de: {selected_excel}")
    
    # Carregar dados do Excel
    try:
        # Carregar todas as planilhas do arquivo Excel
        dfs = get_excel_data(file_path)
        
        # Selecionar a primeira planilha para análise
        first_sheet = list(dfs.keys())[0]
        df = dfs[first_sheet]
        
        # Exibir informações sobre o dataframe
        st.info(f"Analisando a planilha '{first_sheet}' com {df.shape[0]} linhas e {df.shape[1]} colunas")
        
        # Verificar se o dataframe tem as colunas esperadas
        expected_columns = ['timestamp', 'speaker', 'text']
        has_expected_columns = all(col in df.columns for col in expected_columns)
        
        if has_expected_columns:
            # Análises e visualizações
            st.markdown("## 📊 Análises e Visualizações")
            
            # Criar abas para diferentes tipos de análise
            tab1, tab2, tab3, tab4 = st.tabs(["📝 Visão Geral", "👥 Análise de Participação", 
                                             "🔤 Análise de Texto", "📈 Tendências e Padrões"])
            
            with tab1:
                st.markdown("### Visão Geral da Reunião")
                
                # Estatísticas básicas
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total_speakers = df['speaker'].nunique()
                    st.metric("Total de Participantes", total_speakers)
                
                with col2:
                    total_utterances = len(df)
                    st.metric("Total de Falas", total_utterances)
                
                with col3:
                    # Calcular duração aproximada da reunião
                    if 'timestamp' in df.columns and len(df) > 0:
                        try:
                            # Tentar converter para datetime se for string
                            if isinstance(df['timestamp'].iloc[0], str):
                                df['timestamp'] = pd.to_datetime(df['timestamp'])
                            
                            duration = df['timestamp'].max() - df['timestamp'].min()
                            duration_minutes = duration.total_seconds() / 60
                            st.metric("Duração Aproximada", f"{duration_minutes:.1f} min")
                        except:
                            st.metric("Duração", "Não disponível")
                    else:
                        st.metric("Duração", "Não disponível")
                
                # Gráfico de distribuição de falas ao longo do tempo
                st.markdown("#### Distribuição de Falas ao Longo do Tempo")
                
                try:
                    # Criar um histograma de falas ao longo do tempo
                    if 'timestamp' in df.columns:
                        fig = px.histogram(df, x='timestamp', nbins=20, 
                                         title="Distribuição de Falas ao Longo da Reunião")
                        fig.update_layout(xaxis_title="Tempo", yaxis_title="Número de Falas")
                        st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Não foi possível criar o gráfico de distribuição temporal: {e}")
            
            with tab2:
                st.markdown("### Análise de Participação")
                
                # Contagem de falas por participante
                speaker_counts = df['speaker'].value_counts().reset_index()
                speaker_counts.columns = ['Participante', 'Número de Falas']
                
                # Gráfico de barras de participação
                fig = px.bar(speaker_counts, x='Participante', y='Número de Falas',
                           title="Número de Falas por Participante",
                           color='Número de Falas', color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
                
                # Análise de tempo de fala por participante
                st.markdown("#### Tempo de Fala por Participante")
                
                # Calcular o comprimento do texto como proxy para tempo de fala
                df['text_length'] = df['text'].str.len()
                speaker_text_length = df.groupby('speaker')['text_length'].sum().reset_index()
                speaker_text_length.columns = ['Participante', 'Comprimento do Texto']
                
                # Normalizar para percentual
                total_length = speaker_text_length['Comprimento do Texto'].sum()
                speaker_text_length['Percentual'] = (speaker_text_length['Comprimento do Texto'] / total_length * 100).round(1)
                
                # Gráfico de pizza de tempo de fala
                fig = px.pie(speaker_text_length, values='Percentual', names='Participante',
                           title="Distribuição do Tempo de Fala (%)",
                           hover_data=['Comprimento do Texto'])
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
                
                # Tabela de estatísticas de participação
                st.markdown("#### Estatísticas Detalhadas de Participação")
                
                # Juntar contagem de falas e comprimento de texto
                participation_stats = pd.merge(speaker_counts, speaker_text_length, on='Participante')
                participation_stats['Média de Caracteres por Fala'] = (participation_stats['Comprimento do Texto'] / 
                                                                    participation_stats['Número de Falas']).round(1)
                
                # Ordenar por número de falas
                participation_stats = participation_stats.sort_values('Número de Falas', ascending=False)
                
                # Exibir tabela
                st.dataframe(participation_stats)
            
            with tab3:
                st.markdown("### Análise de Texto")
                
                # Combinar todo o texto para análise
                all_text = ' '.join(df['text'].dropna())
                
                # Estatísticas básicas de texto
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total_words = len(all_text.split())
                    st.metric("Total de Palavras", f"{total_words:,}")
                
                with col2:
                    unique_words = len(set(all_text.lower().split()))
                    st.metric("Palavras Únicas", f"{unique_words:,}")
                
                with col3:
                    lexical_diversity = unique_words / total_words if total_words > 0 else 0
                    st.metric("Diversidade Lexical", f"{lexical_diversity:.2f}")
                
                # Processamento de texto para análise
                processed_tokens = process_text(all_text)
                word_freq = Counter(processed_tokens)
                
                # Palavras mais frequentes
                st.markdown("#### Palavras Mais Frequentes")
                
                # Obter as 20 palavras mais comuns
                most_common_words = word_freq.most_common(20)
                words_df = pd.DataFrame(most_common_words, columns=['Palavra', 'Frequência'])
                
                # Gráfico de barras horizontais
                fig = px.bar(words_df, y='Palavra', x='Frequência', orientation='h',
                           title="20 Palavras Mais Frequentes",
                           color='Frequência', color_continuous_scale='Viridis')
                fig.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
                
                # Nuvem de palavras
                st.markdown("#### Nuvem de Palavras")
                
                try:
                    # Criar texto para nuvem de palavras
                    wordcloud_text = ' '.join(processed_tokens)
                    
                    # Gerar nuvem de palavras
                    fig = create_wordcloud(wordcloud_text, title="Nuvem de Palavras da Reunião")
                    st.pyplot(fig)
                except Exception as e:
                    st.error(f"Não foi possível criar a nuvem de palavras: {e}")
                    st.info("Instale a biblioteca wordcloud com 'pip install wordcloud' para habilitar esta funcionalidade.")
                
                # Análise de sentimento por participante
                st.markdown("#### Análise de Sentimento por Participante")
                
                # Calcular sentimento para cada fala
                df['sentiment'] = df['text'].apply(analyze_sentiment)
                
                # Calcular sentimento médio por participante
                sentiment_by_speaker = df.groupby('speaker')['sentiment'].mean().reset_index()
                sentiment_by_speaker.columns = ['Participante', 'Sentimento Médio']
                
                # Gráfico de barras de sentimento
                fig = px.bar(sentiment_by_speaker, x='Participante', y='Sentimento Médio',
                           title="Sentimento Médio por Participante",
                           color='Sentimento Médio', color_continuous_scale='RdBu',
                           range_color=[-1, 1])
                fig.update_layout(yaxis_range=[-1, 1])
                st.plotly_chart(fig, use_container_width=True)
                
                st.info("Nota: Esta é uma análise de sentimento simplificada. Para resultados mais precisos, seria necessário utilizar modelos de NLP mais avançados.")
            
            with tab4:
                st.markdown("### Tendências e Padrões")
                
                # Análise de interações entre participantes
                st.markdown("#### Padrão de Interações")
                
                # Criar uma sequência de falantes
                speaker_sequence = df['speaker'].tolist()
                
                # Contar transições entre falantes
                transitions = []
                for i in range(len(speaker_sequence) - 1):
                    transitions.append((speaker_sequence[i], speaker_sequence[i+1]))
                
                transition_counts = Counter(transitions)
                
                # Criar matriz de adjacência para visualização
                unique_speakers = sorted(df['speaker'].unique())
                n_speakers = len(unique_speakers)
                
                # Criar dataframe para heatmap
                interaction_matrix = pd.DataFrame(0, index=unique_speakers, columns=unique_speakers)
                
                for (speaker1, speaker2), count in transition_counts.items():
                    interaction_matrix.loc[speaker1, speaker2] = count
                
                # Criar heatmap
                fig = px.imshow(interaction_matrix, 
                              labels=dict(x="Próximo Falante", y="Falante Atual", color="Número de Transições"),
                              x=unique_speakers,
                              y=unique_speakers,
                              color_continuous_scale="Viridis")
                
                fig.update_layout(title="Padrão de Interações entre Participantes")
                st.plotly_chart(fig, use_container_width=True)
                
                # Análise de tópicos ao longo do tempo (simplificada)
                st.markdown("#### Evolução de Temas ao Longo da Reunião")
                
                # Dividir a reunião em segmentos
                n_segments = 5
                df_segments = [df.iloc[i*len(df)//n_segments:(i+1)*len(df)//n_segments] for i in range(n_segments)]
                
                # Extrair palavras-chave para cada segmento
                segment_keywords = []
                
                for i, segment in enumerate(df_segments):
                    # Combinar texto do segmento
                    segment_text = ' '.join(segment['text'].dropna())
                    
                    # Processar texto
                    segment_tokens = process_text(segment_text)
                    segment_freq = Counter(segment_tokens)
                    
                    # Obter as 5 palavras mais comuns
                    top_words = [word for word, _ in segment_freq.most_common(5)]
                    
                    # Adicionar ao resultado
                    segment_keywords.append({
                        'Segmento': f"Segmento {i+1}",
                        'Palavras-chave': ", ".join(top_words)
                    })
                
                # Criar dataframe
                keywords_df = pd.DataFrame(segment_keywords)
                
                # Exibir tabela
                st.table(keywords_df)
                
                # Análise de complexidade do discurso
                st.markdown("#### Complexidade do Discurso por Participante")
                
                # Calcular comprimento médio das frases por participante
                df['sentence_count'] = df['text'].apply(lambda x: len(re.split(r'[.!?]+', x)))
                df['words_per_sentence'] = df['text'].apply(lambda x: len(x.split()) / max(1, len(re.split(r'[.!?]+', x))))
                
                # Agrupar por participante
                complexity_by_speaker = df.groupby('speaker')['words_per_sentence'].mean().reset_index()
                complexity_by_speaker.columns = ['Participante', 'Palavras por Frase']
                
                # Gráfico de barras
                fig = px.bar(complexity_by_speaker, x='Participante', y='Palavras por Frase',
                           title="Complexidade do Discurso por Participante",
                           color='Palavras por Frase', color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.warning("O formato do arquivo não corresponde ao esperado para análise. Verifique se o arquivo contém as colunas: 'timestamp', 'speaker' e 'text'.")
            
            # Mostrar as colunas disponíveis
            st.info(f"Colunas disponíveis no arquivo: {', '.join(df.columns)}")
            
            # Exibir uma amostra dos dados
            st.subheader("Amostra dos Dados")
            st.dataframe(df.head())
    
    except Exception as e:
        st.error(f"Erro ao carregar ou analisar o arquivo Excel: {e}")
        st.exception(e)

else:
    st.info("Selecione um arquivo Excel no menu lateral para começar a análise.")

# Rodapé
st.sidebar.markdown("---")
st.sidebar.info("Esta página permite analisar os dados das transcrições de reuniões.")