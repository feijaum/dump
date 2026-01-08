import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# Configurações Visuais e Título do Projeto
st.set_page_config(page_title="BACKUP DOS CLIENTES", page_icon="📊", layout="wide")

st.title("📊 BACKUP DOS CLIENTES - Dashboard")

# --- CONEXÃO COM A PLANILHA DO GOOGLE ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQMAr0iEgRF6pg_wnN9tGFMA9-hKohffXWMhr5IvNjXkxHrs1_u5j22JNuKOII0sQRdGQKT7Fjn-qZS/pub?output=csv"

# --- CARREGAR DICIONÁRIO DO EXCEL ---
def load_client_dictionary():
    """Lê o arquivo clientes.xlsx para mapear os nomes."""
    excel_path = "clientes.xlsx"
    if os.path.exists(excel_path):
        try:
            # Espera-se um Excel com colunas: "Hash" e "Nome"
            df_dict = pd.read_excel(excel_path)
            # Converte para dicionário para busca rápida
            return dict(zip(df_dict['Hash'], df_dict['Nome']))
        except Exception as e:
            st.sidebar.error(f"Erro ao ler clientes.xlsx: {e}")
            return {}
    else:
        st.sidebar.warning("Arquivo 'clientes.xlsx' não encontrado na pasta do app.")
        return {}

@st.cache_data(ttl=300)
def load_data():
    try:
        # Carregar dados do Google Sheets
        df = pd.read_csv(CSV_URL)
        if df.empty: return None

        # Mapeamento por posição das colunas do Google Forms
        new_cols = ['Data_Envio', 'Hardware_Hash', 'Status', 'Arquivo', 'Data_Backup_Info']
        current_cols = list(df.columns)
        mapping = {current_cols[i]: new_cols[i] for i in range(len(new_cols)) if i < len(current_cols)}
        df = df.rename(columns=mapping)
        
        # Tratamento de Datas
        df['Data_Envio'] = pd.to_datetime(df['Data_Envio'], errors='coerce')
        df['Data_Backup_DT'] = pd.to_datetime(df['Data_Backup_Info'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
        
        # REGISTRO ÚNICO POR CLIENTE (O mais recente)
        df_latest = df.sort_values('Data_Envio', ascending=False).drop_duplicates('Hardware_Hash', keep='first')
        
        # Carregar Dicionário Externo (Excel)
        dict_clientes = load_client_dictionary()
        
        # Aplicar o Mapeamento
        df_latest['Nome_Cliente'] = df_latest['Hardware_Hash'].map(dict_clientes).fillna("DESCONHECIDO (Novo Cliente)")
        
        return df_latest
    except Exception as e:
        st.error(f"Erro ao carregar dados da nuvem: {e}")
        return None

df_clientes = load_data()

if df_clientes is not None:
    # Lógica de Status: Alerta se o backup tem mais de 24 horas
    agora = datetime.now()
    limite = agora - timedelta(hours=24)
    
    total = len(df_clientes)
    em_dia = len(df_clientes[df_clientes['Data_Backup_DT'] > limite])
    atrasados = total - em_dia

    # Layout de Métricas
    c1, c2, c3 = st.columns(3)
    c1.metric("Clientes Monitorados", total)
    c2.metric("Backups em Dia", em_dia)
    c3.metric("Clientes em Alerta", atrasados, delta_color="inverse")

    st.divider()

    # Tabela formatada
    st.subheader("📋 Status dos Clientes")
    
    # Reorganizar colunas para exibição
    cols_view = ['Nome_Cliente', 'Status', 'Arquivo', 'Data_Backup_Info', 'Data_Envio', 'Hardware_Hash']
    
    def highlight_rows(row):
        is_late = pd.isna(row.Data_Backup_DT) or row.Data_Backup_DT < limite
        is_error = str(row.Status).upper() == "ERRO"
        if is_late or is_error:
            return ['background-color: #ffcccc'] * len(row)
        return [''] * len(row)

    st.dataframe(
        df_clientes[cols_view].style.apply(highlight_rows, axis=1),
        use_container_width=True
    )
    
    # Barra lateral com instruções
    st.sidebar.info("""
    ### 📂 Dicionário Excel
    Crie um arquivo chamado **clientes.xlsx** na mesma pasta deste script com:
    - Coluna A: **Hash** (Código do hardware)
    - Coluna B: **Nome** (Nome do cliente)
    """)
    
    if st.button("🔄 Atualizar Painel"):
        st.cache_data.clear()
        st.rerun()
else:
    st.info("Nenhum dado recebido ainda ou erro de conexão.")
