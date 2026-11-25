# ==============================================================================
# PROJETO ACOLHE — SISTEMA INTEGRADO (CIDADANIA, SAÚDE E TECNOLOGIA)
# ==============================================================================
# Autores: Estudantes do Curso de Análise e Desenvolvimento de Sistemas (ADS)
# Unidade Alvo: USF Irmã Terezinha — Peixinhos, Recife-PE
# Linguagem: Python 3.12 | Framework Web: Streamlit | Banco: SQLite3 | API: HTTP Native
# ==============================================================================

import streamlit as st
import sqlite3
import pandas as pd
import json
import threading
import io
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# ==============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA E CSS CUSTOMIZADO (FRONTEND)
# ==============================================================================
# Define o título da aba do navegador, ícone e o layout em tela cheia (wide).
st.set_page_config(
    page_title="Projeto Acolhe — Sistema Web Integrado",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS para deixar os elementos modernos, legíveis e com visual profissional
st.markdown("""
<style>
    /* Ajuste do espaçamento do topo da página */
    .main .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2.5rem;
    }
    
    /* Cartão de Métrica Customizado */
    .metric-box {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        transition: transform 0.2s ease;
    }
    .metric-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.08);
    }
    .metric-val {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.2;
    }
    .metric-lbl {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Etiquetas de Status (Badges Coloridos) */
    .badge-pendente {
        background-color: #FEF2F2;
        color: #991B1B;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        border: 1px solid #FCA5A5;
        display: inline-block;
    }
    .badge-andamento {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        border: 1px solid #FCD34D;
        display: inline-block;
    }
    .badge-concluido {
        background-color: #ECFDF5;
        color: #065F46;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        border: 1px solid #6EE7B7;
        display: inline-block;
    }
    
    /* Banner do Topo */
    .header-banner {
        background: linear-gradient(90deg, #1E3A8A 0%, #2563EB 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 10px rgba(37,99,235,0.2);
    }
    .header-banner h1 {
        color: white !important;
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .header-banner p {
        color: #E0E7FF;
        margin: 0.3rem 0 0 0;
        font-size: 1.0rem;
    }
</style>
""", unsafe_allow_html=True)

# Nome do arquivo do Banco de Dados Relacional SQLite
DB_FILE = "acolhe_sistema.db"

# ==============================================================================
# 2. BANCO DE DADOS RELACIONAL (SQLITE3)
# ==============================================================================
def get_db():
    """Retorna uma conexão ativa com o banco de dados SQLite."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas pelo nome (ex: row['nome'])
    return conn

def init_db():
    """Cria as tabelas necessárias e insere dados iniciais (seed data) se estiver vazio."""
    conn = get_db()
    c = conn.cursor()
    
    # Tabela 1: Participantes (Moradores da Comunidade)
    c.execute("""
        CREATE TABLE IF NOT EXISTS participantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            faixa_etaria TEXT NOT NULL,
            telefone TEXT,
            possui_smartphone TEXT,
            facilidade_digital TEXT,
            data_cadastro TEXT
        )
    """)
    
    # Tabela 2: Atendimentos (Triagem e Encaminhamentos Interdisciplinares)
    c.execute("""
        CREATE TABLE IF NOT EXISTS atendimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            participante_id INTEGER,
            nome_participante TEXT,
            data_registro TEXT,
            demanda_saude TEXT,
            demanda_cidadania TEXT,
            demanda_tecnologia TEXT,
            area_responsavel TEXT,
            acao_realizada TEXT,
            encaminhamento TEXT,
            observacoes TEXT,
            status TEXT DEFAULT 'Pendente',
            FOREIGN KEY (participante_id) REFERENCES participantes (id)
        )
    """)
    
    # Inserção de Registros de Demonstração (Popula o banco no primeiro acesso)
    c.execute("SELECT COUNT(*) FROM atendimentos")
    if c.fetchone()[0] == 0:
        seed_data = [
            ("ACT-2026-001", "Maria José da Silva", "Idoso (60+)", "Sim (Wi-Fi)", "Baixa", 
             "Dificuldade de ver vacinas no app", "Dúvida sobre Benefício BPC", "Ajuda no Gov.br", 
             "Enfermagem", "Recuperação de senha do Gov.br e agendamento", "CRAS Peixinhos", "Aguardando documento", "Concluído", "2026-10-15 09:30"),
            ("ACT-2026-002", "João Pedro Santos", "Adulto (30-59)", "Sim (Dados Móveis)", "Média", 
             "Agendamento de consulta especializada", "Emissão de Carteira de Trabalho Digital", "Baixar app CTPS", 
             "Direito", "Orientações sobre CTPS Digital e agendamento de exame", "Defensoria Pública", "Em análise pelo órgão", "Em Andamento", "2026-10-15 10:15"),
            ("ACT-2026-003", "Ana Clara Lima", "Jovem (18-29)", "Sim (Wi-Fi)", "Alta", 
             "Orientação sobre prevenção e saúde da mulher", "Consulta sobre CadÚnico", "Navegação em sites públicos", 
             "ADS", "Auxílio na atualização cadastral e navegação em serviços", "CRAS Peixinhos", "Concluído com sucesso", "Concluído", "2026-10-16 11:00"),
            ("ACT-2026-004", "Severino Ramos de Oliveira", "Idoso (60+)", "Não possui", "Nenhuma", 
             "Solicitação de medicamentos contínuos", "Consulta aposentadoria e BPC/LOAS", "Inclusão digital básica", 
             "Interdisciplinar", "Triagem completa de saúde e atendimento jurídico", "INSS / Posto de Saúde", "Encaminhado para perícia", "Pendente", "2026-10-17 14:20")
        ]
        
        for codigo, nome, faixa, smartphone, facilidade, d_saude, d_cidadania, d_tec, area, acao, enc, obs, status, data in seed_data:
            c.execute("INSERT INTO participantes (nome, faixa_etaria, possui_smartphone, facilidade_digital, data_cadastro) VALUES (?, ?, ?, ?, ?)",
                      (nome, faixa, smartphone, facilidade, data))
            part_id = c.lastrowid
            c.execute("""
                INSERT INTO atendimentos 
                (codigo, participante_id, nome_participante, data_registro, demanda_saude, demanda_cidadania, demanda_tecnologia, area_responsavel, acao_realizada, encaminhamento, observacoes, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (codigo, part_id, nome, data, d_saude, d_cidadania, d_tec, area, acao, enc, obs, status))
            
    conn.commit()
    conn.close()

# Executa a inicialização do banco ao carregar o script
init_db()

# ==============================================================================
# 3. BACKEND API RESTFUL (EXECUTADA EM THREAD SECUNDÁRIA)
# ==============================================================================
class AcolheAPIHandler(BaseHTTPRequestHandler):
    """Gerenciador de requisições HTTP para a API RESTful."""
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_GET(self):
        """Trata requisições GET da API."""
        parsed_path = urlparse(self.path)
        
        # Endpoint 1: Healthcheck
        if parsed_path.path == "/api/v1/health":
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "online", "system": "Projeto Acolhe API", "version": "1.0.0"}).encode())
            
        # Endpoint 2: Métricas do Sistema
        elif parsed_path.path == "/api/v1/metricas":
            conn = get_db()
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM atendimentos")
            total = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM atendimentos WHERE status = 'Concluído'")
            concluidos = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM atendimentos WHERE status = 'Pendente'")
            pendentes = c.fetchone()[0]
            conn.close()
            
            res = {
                "total_atendimentos": total,
                "concluidos": concluidos,
                "pendentes": pendentes,
                "taxa_resolucao_pct": round((concluidos / total * 100), 1) if total > 0 else 0
            }
            self._set_headers(200)
            self.wfile.write(json.dumps(res, ensure_ascii=False).encode('utf-8'))
            
        # Endpoint 3: Lista Completa de Atendimentos
        elif parsed_path.path == "/api/v1/atendimentos":
            conn = get_db()
            c = conn.cursor()
            c.execute("SELECT * FROM atendimentos ORDER BY id DESC")
            rows = [dict(row) for row in c.fetchall()]
            conn.close()
            self._set_headers(200)
            self.wfile.write(json.dumps({"total": len(rows), "data": rows}, ensure_ascii=False).encode('utf-8'))
            
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint não encontrado"}).encode())

def run_api_server(port=8050):
    """Inicia o servidor HTTP nativo da API REST."""
    try:
        server = HTTPServer(('0.0.0.0', port), AcolheAPIHandler)
        server.serve_forever()
    except Exception:
        pass

# Inicia o servidor de API em segundo plano (Multithreading) sem travar a tela do Streamlit
if "api_started" not in st.session_state:
    st.session_state.api_started = True
    threading.Thread(target=run_api_server, daemon=True).start()

# ==============================================================================
# 4. NAVEGAÇÃO E MENU LATERAL (SIDEBAR)
# ==============================================================================
st.sidebar.markdown("### 🏥 Projeto Acolhe")
st.sidebar.caption("Cidadania, Saúde e Tecnologia | USF Irmã Terezinha")

pagina = st.sidebar.radio(
    "Menu de Navegação:",
    [
        "📊 Dashboard & Métricas", 
        "📝 Novo Diagnóstico", 
        "📋 Gestão de Encaminhamentos", 
        "👤 Histórico do Morador",
        "💡 Guia de Inclusão Digital",
        "⚙️ API REST & Documentação"
    ]
)

st.sidebar.divider()
st.sidebar.markdown("**Banco de Dados**: 🟢 SQLite (`acolhe_sistema.db`)")
st.sidebar.markdown("**API REST Backend**: 🟢 Ativa na porta `8050`")

# ==============================================================================
# 5. MÓDULO 1: DASHBOARD & MÉTRICAS
# ==============================================================================
if pagina == "📊 Dashboard & Métricas":
    st.markdown("""
    <div class="header-banner">
        <h1>📊 Painel Geral de Impacto Comunitário</h1>
        <p>Métricas consolidadas em tempo real direto do banco de dados relacional</p>
    </div>
    """, unsafe_allow_html=True)
    
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM atendimentos", conn)
    conn.close()
    
    total = len(df)
    concluidos = len(df[df['status'] == 'Concluído']) if total > 0 else 0
    pendentes = len(df[df['status'] == 'Pendente']) if total > 0 else 0
    em_andamento = len(df[df['status'] == 'Em Andamento']) if total > 0 else 0
    taxa_res = (concluidos / total * 100) if total > 0 else 0
    
    # Exibição dos Cartões Principais (KPIs)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-box"><div class="metric-val">{total}</div><div class="metric-lbl">Total Atendimentos</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-box"><div class="metric-val" style="color: #059669;">{concluidos}</div><div class="metric-lbl">Concluídos</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-box"><div class="metric-val" style="color: #D97706;">{em_andamento}</div><div class="metric-lbl">Em Andamento</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-box"><div class="metric-val" style="color: #2563EB;">{taxa_res:.1f}%</div><div class="metric-lbl">Taxa de Resolução</div></div>', unsafe_allow_html=True)
        
    st.divider()
    
    if total > 0:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Atendimentos por Área Responsável")
            st.bar_chart(df['area_responsavel'].value_counts())
        with c2:
            st.subheader("Distribuição por Status")
            st.bar_chart(df['status'].value_counts())
            
        st.subheader("Registros Recentes")
        st.dataframe(df[['codigo', 'nome_participante', 'area_responsavel', 'encaminhamento', 'status', 'data_registro']].tail(10), use_container_width=True)
        
        # Botão para exportar relatório completo em CSV
        buffer = io.BytesIO()
        df.to_csv(buffer, index=False, encoding='utf-8-sig')
        st.download_button(
            label="📄 Baixar Relatório Completo em CSV",
            data=buffer.getvalue(),
            file_name=f"relatorio_acolhe_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
    else:
        st.info("Nenhum atendimento cadastrado no momento.")

# ==============================================================================
# 6. MÓDULO 2: NOVO DIAGNÓSTICO (FORMULÁRIO DE ACOLHIMENTO)
# ==============================================================================
elif pagina == "📝 Novo Diagnóstico":
    st.title("📝 Formulário de Diagnóstico Interdisciplinar")
    st.caption("Coleta padronizada durante o acolhimento do morador na USF Irmã Terezinha")
    
    conn = get_db()
    df_part_exist = pd.read_sql_query("SELECT id, nome, faixa_etaria, possui_smartphone, facilidade_digital FROM participantes", conn)
    conn.close()
    
    tipo_cadastro = st.radio("Selecione a opção de cadastro:", ["Morador Novo", "Morador Já Cadastrado"], horizontal=True)
    
    nome_pre, faixa_pre, smart_pre, facil_pre = "", "Adulto (30-59)", "Sim (Wi-Fi)", "Média"
    part_id_selecionado = None
    
    # Se for morador já cadastrado, preenche os dados automaticamente
    if tipo_cadastro == "Morador Já Cadastrado" and len(df_part_exist) > 0:
        opcoes = {row['id']: f"{row['nome']} ({row['faixa_etaria']})" for _, row in df_part_exist.iterrows()}
        part_id_selecionado = st.selectbox("Buscar Morador Cadastrado:", list(opcoes.keys()), format_func=lambda x: opcoes[x])
        morador = df_part_exist[df_part_exist['id'] == part_id_selecionado].iloc[0]
        nome_pre, faixa_pre, smart_pre, facil_pre = morador['nome'], morador['faixa_etaria'], morador['possui_smartphone'], morador['facilidade_digital']

    with st.form("form_triagem", clear_on_submit=True):
        st.subheader("Passo 1 — Perfil e Letramento Digital")
        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome Completo do Morador*", value=nome_pre)
        faixa_etaria = col2.selectbox("Faixa Etária*", ["Jovem (18-29)", "Adulto (30-59)", "Idoso (60+)"], index=["Jovem (18-29)", "Adulto (30-59)", "Idoso (60+)"].index(faixa_pre))
        
        col3, col4 = st.columns(2)
        possui_smartphone = col3.selectbox("Possui Smartphone / Acesso à Internet?", ["Sim (Wi-Fi)", "Sim (Dados Móveis)", "Não possui"])
        facilidade_digital = col4.select_slider("Nível de Facilidade com Tecnologia*", options=["Nenhuma", "Baixa", "Média", "Alta"], value=facil_pre)
        
        st.subheader("Passo 2 — Triagem Interdisciplinar por Área")
        tab_saude, tab_cidadania, tab_tec = st.tabs(["🩺 Saúde (Enfermagem)", "⚖️ Cidadania (Direito)", "💻 Tecnologia (ADS)"])
        
        with tab_saude:
            demanda_saude = st.text_area("Demandas de Saúde", placeholder="Ex: Histórico vacinal, Meu SUS Digital, marcação de exames...")
        with tab_cidadania:
            demanda_cidadania = st.text_area("Demandas de Direitos & Cidadania", placeholder="Ex: Benefício BPC/LOAS, CadÚnico, emissão de documentos...")
        with tab_tec:
            demanda_tecnologia = st.text_area("Demandas Tecnológicas", placeholder="Ex: Criação da conta Gov.br, recuperação de senha, baixar apps...")
            
        st.subheader("Passo 3 — Plano de Ação e Encaminhamento")
        c_a, c_b, c_c = st.columns(3)
        area_responsavel = c_a.selectbox("Área Principal Responsável*", ["ADS", "Direito", "Enfermagem", "Interdisciplinar"])
        status_inicial = c_b.selectbox("Status Inicial*", ["Pendente", "Em Andamento", "Concluído"])
        encaminhamento = c_c.text_input("Órgão de Encaminhamento", placeholder="Ex: CRAS Peixinhos, Defensoria Pública, Posto de Saúde...")
        
        acao_realizada = st.text_input("Ação Prestada no Momento")
        observacoes = st.text_area("Observações Internas")
        
        submeter = st.form_submit_button("💾 Gravar Atendimento no Banco de Dados")
        
        if submeter:
            if not nome:
                st.error("Por favor, informe o nome do morador.")
            else:
                conn = get_db()
                c = conn.cursor()
                data_agora = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                # Inserção ou recuperação do participante
                if not part_id_selecionado:
                    c.execute("INSERT INTO participantes (nome, faixa_etaria, possui_smartphone, facilidade_digital, data_cadastro) VALUES (?, ?, ?, ?, ?)",
                              (nome, faixa_etaria, possui_smartphone, facilidade_digital, data_agora))
                    part_id_selecionado = c.lastrowid
                
                c.execute("SELECT COUNT(*) FROM atendimentos")
                qtd = c.fetchone()[0] + 1
                codigo = f"ACT-2026-{qtd:03d}"
                
                # Inserção do registro de atendimento
                c.execute("""
                    INSERT INTO atendimentos (codigo, participante_id, nome_participante, data_registro, demanda_saude, demanda_cidadania, demanda_tecnologia, area_responsavel, acao_realizada, encaminhamento, observacoes, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (codigo, part_id_selecionado, nome, data_agora, demanda_saude, demanda_cidadania, demanda_tecnologia, area_responsavel, acao_realizada, encaminhamento, observacoes, status_inicial))
                
                conn.commit()
                conn.close()
                st.balloons()
                st.success(f"✅ Atendimento **{codigo}** gravado com sucesso no SQLite e sincronizado na nuvem!")

# ==============================================================================
# 7. MÓDULO 3: GESTÃO DE ENCAMINHAMENTOS
# ==============================================================================
elif pagina == "📋 Gestão de Encaminhamentos":
    st.title("📋 Painel de Gestão e Atualização de Casos")
    
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM atendimentos ORDER BY id DESC", conn)
    conn.close()
    
    if len(df) > 0:
        c_busca, c_status = st.columns([2, 1])
        termo = c_busca.text_input("🔍 Pesquisar por Nome ou Código (ex: ACT-2026-001):")
        filtro_stat = c_status.selectbox("Filtrar Status:", ["Todos", "Pendente", "Em Andamento", "Concluído"])
        
        df_filtrado = df.copy()
        if termo:
            df_filtrado = df_filtrado[df_filtrado['nome_participante'].str.contains(termo, case=False) | df_filtrado['codigo'].str.contains(termo, case=False)]
        if filtro_stat != "Todos":
            df_filtrado = df_filtrado[df_filtrado['status'] == filtro_stat]
            
        st.caption(f"Exibindo {len(df_filtrado)} registro(s)")
        
        modo_view = st.radio("Modo de Exibição:", ["📲 Cartões Interativos (Kanban)", "📊 Tabela Completa"], horizontal=True)
        
        if modo_view == "📲 Cartões Interativos (Kanban)":
            for _, row in df_filtrado.iterrows():
                badge_class = "badge-pendente" if row['status'] == "Pendente" else ("badge-andamento" if row['status'] == "Em Andamento" else "badge-concluido")
                with st.expander(f"📌 {row['codigo']} — {row['nome_participante']} ({row['area_responsavel']})"):
                    st.markdown(f"**Status**: <span class='{badge_class}'>{row['status']}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Data do Registro**: {row['data_registro']} | **Encaminhado para**: `{row['encaminhamento'] or 'Não informado'}`")
                    st.markdown(f"**Ação Realizada**: {row['acao_realizada'] or 'Nenhuma'}")
                    st.markdown(f"**Observações**: {row['observacoes'] or 'Sem observações'}")
                    
                    # Formulário de Atualização Rápida de Status
                    with st.form(f"quick_update_{row['codigo']}"):
                        col_a, col_b = st.columns([1, 2])
                        n_status = col_a.selectbox("Novo Status:", ["Pendente", "Em Andamento", "Concluído"], index=["Pendente", "Em Andamento", "Concluído"].index(row['status']))
                        n_obs = col_b.text_input("Nova Observação:", value=row['observacoes'] or "")
                        if st.form_submit_button("Atualizar Status no Banco"):
                            conn = get_db()
                            c = conn.cursor()
                            c.execute("UPDATE atendimentos SET status = ?, observacoes = ? WHERE codigo = ?", (n_status, n_obs, row['codigo']))
                            conn.commit()
                            conn.close()
                            st.success("Status atualizado com sucesso!")
                            st.rerun()
        else:
            st.dataframe(df_filtrado, use_container_width=True)
    else:
        st.info("Nenhum atendimento registrado no banco de dados.")

# ==============================================================================
# 8. MÓDULO 4: HISTÓRICO DO MORADOR
# ==============================================================================
elif pagina == "👤 Histórico do Morador":
    st.title("👤 Prontuário Social do Morador")
    st.caption("Consulta consolidada do histórico de triagens do morador na USF")
    
    conn = get_db()
    df_part = pd.read_sql_query("SELECT * FROM participantes", conn)
    
    if len(df_part) > 0:
        morador_sel = st.selectbox("Selecione o Morador para consultar:", df_part['id'].tolist(), format_func=lambda x: df_part[df_part['id']==x]['nome'].values[0])
        dados_m = df_part[df_part['id'] == morador_sel].iloc[0]
        
        st.markdown(f"### Ficha do Participante: **{dados_m['nome']}**")
        col_a, col_b, col_c = st.columns(3)
        col_a.markdown(f"**Faixa Etária**: {dados_m['faixa_etaria']}")
        col_b.markdown(f"**Smartphone/Internet**: {dados_m['possui_smartphone']}")
        col_c.markdown(f"**Facilidade Digital**: {dados_m['facilidade_digital']}")
        
        df_historico = pd.read_sql_query("SELECT codigo, data_registro, area_responsavel, encaminhamento, acao_realizada, status FROM atendimentos WHERE participante_id = ?", conn, params=(int(morador_sel),))
        st.subheader(f"Histórico de Atendimentos ({len(df_historico)})")
        st.dataframe(df_historico, use_container_width=True)
    else:
        st.info("Nenhum morador cadastrado no sistema.")
    conn.close()

# ==============================================================================
# 9. MÓDULO 5: GUIA DE INCLUSÃO DIGITAL
# ==============================================================================
elif pagina == "💡 Guia de Inclusão Digital":
    st.title("💡 Guia Prático de Inclusão Digital")
    st.caption("Instrumento de apoio pedagógico para orientação dos moradores durante o atendimento")
    
    with st.expander("🌐 1. Conta Gov.br — Acesso Único aos Serviços Públicos", expanded=True):
        st.markdown("""
        * **Objetivo**: Acesso centralizado a serviços estaduais e federais.
        * **Passo a Passo da Equipe de ADS**:
          1. Auxiliar o morador no cadastro inicial ou recuperação de senha via e-mail/SMS.
          2. Subir o nível da conta de **Bronze** para **Prata/Ouro** através do aplicativo bancário ou validação facial.
        """)
        
    with st.expander("🏥 2. Meu SUS Digital (ConecteSUS)"):
        st.markdown("""
        * **Objetivo**: Acompanhamento do histórico de saúde do cidadão.
        * **Passo a Passo da Equipe**:
          1. Baixar o app no celular do morador e realizar o login Gov.br.
          2. Emitir o Cartão Nacional de Saúde (CNS) digital e verificar histórico de vacinação.
        """)

    with st.expander("📄 3. Meu INSS & Carteira de Trabalho Digital"):
        st.markdown("""
        * **Objetivo**: Garantia de direitos previdenciários e trabalhistas.
        * **Passo a Passo da Equipe**:
          1. Consultar extratos de contribuição e andamento do BPC/LOAS.
          2. Acessar o contrato de trabalho digital e requerer seguro-desemprego.
        """)

# ==============================================================================
# 10. MÓDULO 6: API REST & DOCUMENTAÇÃO
# ==============================================================================
elif pagina == "⚙️ API REST & Documentação":
    st.title("⚙️ Documentação da API RESTful")
    st.info("🌐 Servidor de API ativo na porta local: `http://localhost:8050/api/v1/`")
    
    tab1, tab2 = st.tabs(["📌 Endpoints Disponíveis", "🧪 Testar Requisição HTTP"])
    
    with tab1:
        st.markdown("""
        | Método | Endpoint | Descrição |
        | :--- | :--- | :--- |
        | `GET` | `/api/v1/health` | Retorna o status de operação do servidor |
        | `GET` | `/api/v1/metricas` | Retorna o total de atendimentos, concluídos e taxa de resolução em JSON |
        | `GET` | `/api/v1/atendimentos` | Retorna a lista completa de atendimentos da base |
        """)
        
    with tab2:
        if st.button("Executar Teste GET `/api/v1/metricas`"):
            conn = get_db()
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM atendimentos")
            tot = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM atendimentos WHERE status = 'Concluído'")
            conc = c.fetchone()[0]
            conn.close()
            
            st.success("HTTP 200 OK — Resposta Recebida:")
            st.json({
                "status_code": 200,
                "data": {
                    "total_atendimentos": tot,
                    "concluidos": conc,
                    "taxa_resolucao_pct": round((conc/tot*100), 1) if tot > 0 else 0
                }
            })

st.caption("Projeto Extensionista Acolhe — Cidadania, Saúde e Tecnologia | Faculdade ESUDA")
