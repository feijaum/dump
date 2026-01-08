import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configurações Visuais e Título do Projeto
st.set_page_config(page_title="BACKUP DOS CLIENTES", page_icon="📊", layout="wide")

# Estilo customizado para melhorar a visualização
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_index=True)

st.title("📊 BACKUP DOS CLIENTES - Dashboard")
st.markdown("Monitorização centralizada dos logs de backup.")

# --- CONEXÃO COM A PLANILHA DO GOOGLE ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQMAr0iEgRF6pg_wnN9tGFMA9-hKohffXWMhr5IvNjXkxHrs1_u5j22JNuKOII0sQRdGQKT7Fjn-qZS/pub?output=csv"

@st.cache_data(ttl=300)
def load_data():
    try:
        # Carregar dados do Google Sheets
        df = pd.read_csv(CSV_URL)
        if df.empty: return None

        # Mapeamento dinâmico das colunas (Ordem: Timestamp, Hash, Status, Arquivo, Data Backup, Nome Cliente)
        # Se a planilha tiver mais colunas, o mapeamento ignora o resto
        new_cols = ['Data_Envio', 'Hardware_Hash', 'Status', 'Arquivo', 'Data_Backup_Info', 'Nome_Cliente']
        current_cols = list(df.columns)
        
        mapping = {current_cols[i]: new_cols[i] for i in range(len(new_cols)) if i < len(current_cols)}
        df = df.rename(columns=mapping)
        
        # Tratamento de Datas de Envio
        df['Data_Envio'] = pd.to_datetime(df['Data_Envio'], errors='coerce')
        
        # REGISTRO ÚNICO: Pega apenas o último envio de cada cliente
        df_latest = df.sort_values('Data_Envio', ascending=False).drop_duplicates('Hardware_Hash', keep='first').copy()
        
        # Se a coluna Nome_Cliente não existir na planilha ainda, usa o Hash
        if 'Nome_Cliente' not in df_latest.columns:
            df_latest['Nome_Cliente'] = df_latest['Hardware_Hash']
            
        return df_latest
    except Exception as e:
        st.error(f"Erro ao carregar dados da nuvem: {e}")
        return None

def verificar_atraso(row, limite):
    """Lógica para determinar se o cliente está com backup em atraso."""
    try:
        # Tenta converter a data que o cliente enviou
        dt_backup = pd.to_datetime(row['Data_Backup_Info'], dayfirst=True, errors='coerce')
        # Se a data for inválida ou menor que o limite (24h), está atrasado
        if pd.isna(dt_backup) or dt_backup < limite:
            return True
        return False
    except:
        return True

df_clientes = load_data()

if df_clientes is not None:
    # Lógica de Tempo (24 horas)
    agora = datetime.now()
    limite = agora - timedelta(hours=24)
    
    # Processamento de Status
    df_clientes['Atrasado'] = df_clientes.apply(lambda r: verificar_atraso(r, limite), axis=1)
    df_clientes['Status_Erro'] = df_clientes['Status'].astype(str).str.upper() == "ERRO"
    df_clientes['Critico'] = df_clientes['Atrasado'] | df_clientes['Status_Erro']

    # Métricas de Topo
    total = len(df_clientes)
    criticos = df_clientes['Critico'].sum()
    em_dia = total - criticos

    c1, c2, c3 = st.columns(3)
    c1.metric("Clientes Monitorizados", total)
    c2.metric("Backups em Dia", em_dia)
    c3.metric("Clientes em Alerta", int(criticos), delta=f"{int(criticos)} críticos", delta_color="inverse")

    st.divider()

    # Filtro de Busca
    busca = st.text_input("🔍 Procurar por Nome ou Hash", "")
    if busca:
        df_clientes = df_clientes[
            df_clientes['Nome_Cliente'].str.contains(busca, case=False, na=False) | 
            df_clientes['Hardware_Hash'].str.contains(busca, case=False, na=False)
        ]

    st.subheader("📋 Estado Atual dos Clientes")
    
    # Definimos as colunas que queremos mostrar
    cols_to_display = ['Nome_Cliente', 'Status', 'Arquivo', 'Data_Backup_Info', 'Data_Envio', 'Hardware_Hash']
    
    # Função para colorir a linha inteira
    def style_dataframe(row):
        # Se for crítico, aplica fundo vermelho claro
        if row['Critico']:
            return ['background-color: #ffcccc'] * len(row)
        return [''] * len(row)

    # Exibição Final
    # Passamos as colunas extras ('Critico') para o style mas escondemos no st.dataframe
    st.dataframe(
        df_clientes[cols_to_display + ['Critico']].style.apply(style_dataframe, axis=1),
        use_container_width=True,
        column_config={
            "Critico": None, # Esconde a coluna técnica
            "Hardware_Hash": st.column_config.TextColumn("ID Hardware", width="small"),
            "Data_Backup_Info": "Data do Ficheiro",
            "Data_Envio": "Último Reporte"
        },
        hide_index=True
    )
    
    # Botão de refresh manual
    if st.button("🔄 Atualizar Painel"):
        st.cache_data.clear()
        st.rerun()
else:
    st.info("A aguardar o recebimento de dados. Certifica-te de que os clientes estão a correr o serviço.")

st.sidebar.markdown("---")
st.sidebar.markdown("**Dica:** Alimenta a coluna 'Nome_Cliente' diretamente na tua Planilha Google para identificar as máquinas aqui.")
