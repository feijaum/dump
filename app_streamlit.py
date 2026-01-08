import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configurações Visuais e Título do Projeto
st.set_page_config(page_title="BACKUP DOS CLIENTES", page_icon="📊", layout="wide")

st.title("📊 BACKUP DOS CLIENTES - Dashboard")

# --- CONEXÃO COM A PLANILHA DO GOOGLE ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQMAr0iEgRF6pg_wnN9tGFMA9-hKohffXWMhr5IvNjXkxHrs1_u5j22JNuKOII0sQRdGQKT7Fjn-qZS/pub?output=csv"

@st.cache_data(ttl=300)
def load_data():
    try:
        # Carregar dados do Google Sheets
        df = pd.read_csv(CSV_URL)
        if df.empty: return None

        # Mapeamento por posição das colunas para evitar erros de nomes
        # 0: Data Envio, 1: Hash, 2: Status, 3: Arquivo, 4: Data Backup, 5: Nome Cliente
        new_cols = ['Data_Envio', 'Hardware_Hash', 'Status', 'Arquivo', 'Data_Backup_Info', 'Nome_Cliente']
        current_cols = list(df.columns)
        
        mapping = {current_cols[i]: new_cols[i] for i in range(len(new_cols)) if i < len(current_cols)}
        df = df.rename(columns=mapping)
        
        # Tratamento de Datas (Data_Envio é quando o formulário recebeu o dado)
        df['Data_Envio'] = pd.to_datetime(df['Data_Envio'], errors='coerce')
        
        # REGISTRO ÚNICO POR CLIENTE (O mais recente baseado no envio)
        df_latest = df.sort_values('Data_Envio', ascending=False).drop_duplicates('Hardware_Hash', keep='first')
        
        # Se a coluna Nome_Cliente ainda não existir na planilha, usa o Hash
        if 'Nome_Cliente' not in df_latest.columns:
            df_latest['Nome_Cliente'] = df_latest['Hardware_Hash']
            
        return df_latest
    except Exception as e:
        st.error(f"Erro ao carregar dados da nuvem: {e}")
        return None

df_clientes = load_data()

if df_clientes is not None:
    # Lógica de Status: Alerta se o backup tem mais de 24 horas
    agora = datetime.now()
    limite = agora - timedelta(hours=24)
    
    # Calculamos o status de atraso antes de filtrar as colunas para evitar o AttributeError
    def verificar_atraso(row):
        try:
            # Tenta converter a string da data do backup que veio do cliente
            dt_backup = pd.to_datetime(row['Data_Backup_Info'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
            if pd.isna(dt_backup) or dt_backup < limite:
                return True
            return False
        except:
            return True

    # Criamos uma coluna temporária invisível para o estilo
    df_clientes['Atrasado'] = df_clientes.apply(verificar_atraso, axis=1)

    total = len(df_clientes)
    # Conta quantos não estão atrasados
    em_dia = len(df_clientes[df_clientes['Atrasado'] == False])
    atrasados = total - em_dia

    # Layout de Métricas
    c1, c2, c3 = st.columns(3)
    c1.metric("Clientes Monitorados", total)
    c2.metric("Backups em Dia", em_dia)
    c3.metric("Clientes em Alerta", atrasados, delta_color="inverse")

    st.divider()

    # Tabela formatada
    st.subheader("📋 Status dos Clientes")
    
    # Colunas que queremos exibir na ordem correta
    cols_view = ['Nome_Cliente', 'Status', 'Arquivo', 'Data_Backup_Info', 'Data_Envio', 'Hardware_Hash', 'Atrasado']
    cols_to_show = [c for c in cols_view if c in df_clientes.columns]
    
    def highlight_rows(row):
        # Agora usamos a coluna 'Atrasado' que garantimos estar no DataFrame
        is_error = str(row['Status']).upper() == "ERRO"
        if row['Atrasado'] or is_error:
            return ['background-color: #ffcccc'] * len(row)
        return [''] * len(row)

    # Exibimos o DataFrame, mas escondemos a coluna técnica 'Atrasado'
    st.dataframe(
        df_clientes[cols_to_show].style.apply(highlight_rows, axis=1),
        use_container_width=True,
        column_config={
            "Atrasado": None # Isso esconde a coluna da visão do usuário
        }
    )
    
    if st.button("🔄 Atualizar Painel"):
        st.cache_data.clear()
        st.rerun()
else:
    st.info("Aguardando o recebimento de dados ou verificação do link da planilha.")
