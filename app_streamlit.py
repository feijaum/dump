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
    """, unsafe_allow_html=True)

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

        # Mapeamento dinâmico das colunas
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

def definir_status_alerta(row, hoje, ontem):
    """
    Define o nível de alerta:
    0: OK (Verde) - Backup feito hoje
    1: PENDENTE (Amarelo) - Backup feito ontem, mas falta hoje
    2: CRÍTICO (Vermelho) - Backup mais antigo que ontem ou Erro
    """
    try:
        dt_backup = pd.to_datetime(row['Data_Backup_Info'], dayfirst=True, errors='coerce').date()
        status_raw = str(row['Status']).upper()
        
        if status_raw == "ERRO":
            return 2
        
        if pd.isna(dt_backup):
            return 2
            
        if dt_backup == hoje:
            return 0
        elif dt_backup == ontem:
            return 1
        else:
            return 2
    except:
        return 2

df_clientes = load_data()

if df_clientes is not None:
    # Datas de referência
    hoje = datetime.now().date()
    ontem = hoje - timedelta(days=1)
    
    # Processamento de Status de Alerta
    df_clientes['Alerta_Nivel'] = df_clientes.apply(lambda r: definir_status_alerta(r, hoje, ontem), axis=1)

    # Listas para a barra lateral
    clientes_criticos = df_clientes[df_clientes['Alerta_Nivel'] == 2]['Nome_Cliente'].unique().tolist()
    clientes_pendentes = df_clientes[df_clientes['Alerta_Nivel'] == 1]['Nome_Cliente'].unique().tolist()

    # Métricas de Topo
    total = len(df_clientes)
    em_dia_count = (df_clientes['Alerta_Nivel'] == 0).sum()
    pendentes_hoje_count = (df_clientes['Alerta_Nivel'] == 1).sum()
    criticos_count = (df_clientes['Alerta_Nivel'] == 2).sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("Clientes Monitorizados", total)
    c2.metric("Concluídos Hoje", em_dia_count)
    c3.metric("Pendentes Hoje", pendentes_hoje_count, delta=f"{pendentes_hoje_count} hoje", delta_color="off")

    st.divider()

    # Filtro de Busca
    busca = st.text_input("🔍 Procurar por Nome ou Hash", "")
    if busca:
        df_clientes = df_clientes[
            df_clientes['Nome_Cliente'].str.contains(busca, case=False, na=False) | 
            df_clientes['Hardware_Hash'].str.contains(busca, case=False, na=False)
        ]

    st.subheader("📋 Estado Detalhado")
    
    # Colunas para exibição
    cols_to_display = ['Nome_Cliente', 'Status', 'Arquivo', 'Data_Backup_Info', 'Data_Envio', 'Hardware_Hash']
    
    def style_dataframe(row):
        if row['Alerta_Nivel'] == 2:
            return ['background-color: #ffcccc'] * len(row) # Vermelho claro
        elif row['Alerta_Nivel'] == 1:
            return ['background-color: #fff9c4'] * len(row) # Amarelo claro
        return [''] * len(row)

    st.dataframe(
        df_clientes[cols_to_display + ['Alerta_Nivel']].style.apply(style_dataframe, axis=1),
        width="stretch",
        column_config={
            "Alerta_Nivel": None,
            "Hardware_Hash": st.column_config.TextColumn("ID Hardware", width="small"),
            "Data_Backup_Info": "Data do Ficheiro",
            "Data_Envio": "Último Reporte"
        },
        hide_index=True
    )
    
    # --- BARRA LATERAL DINÂMICA ---
    st.sidebar.header("📊 Resumo do Dia")
    
    # Contador de pendentes
    st.sidebar.subheader(f"⏳ Pendentes Hoje: {pendentes_hoje_count}")
    if clientes_pendentes:
        for nome in clientes_pendentes:
            st.sidebar.warning(f"⚠️ {nome}")
    
    st.sidebar.divider()
    
    st.sidebar.subheader(f"🚨 Críticos: {criticos_count}")
    if clientes_criticos:
        for nome in clientes_criticos:
            st.sidebar.error(f"❌ {nome}")
    else:
        st.sidebar.success("✅ Nenhum cliente crítico")

    if st.button("🔄 Atualizar Painel"):
        st.cache_data.clear()
        st.rerun()
else:
    st.info("A aguardar o recebimento de dados.")
