import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date, timedelta
import time
import database as db 

# ==========================================
# DEFINIÇÃO DAS LISTAS (FIXAS NO TOPO)
# ==========================================
LISTA_BANCOS = [
  "001 - Banco do Brasil",
  "003 - Banco da Amazônia",
  "004 - Banco do Nordeste",
  "007 - BNDES",
  "008 - Banco Meridional",
  "021 - Banestes",
  "024 - Banco Bandepe",
  "025 - Banco Alfa",
  "029 - Banco Banerj",
  "033 - Santander",
  "036 - Banco Bradesco BBI",
  "037 - Banco do Estado do Pará",
  "040 - Banco Cargill",
  "041 - Banrisul",
  "047 - Banco do Estado de Sergipe",
  "062 - Hipercard Banco Múltiplo",
  "063 - Banco Bradescard",
  "065 - Banco Andbank",
  "066 - Banco Morgan Stanley",
  "069 - Banco Crefisa",
  "070 - BRB",
  "074 - Banco J. Safra",
  "075 - Banco ABN Amro",
  "077 - Inter",
  "082 - Banco Topázio",
  "085 - Ailos",
  "090 - Unicred",
  "097 - Cresol",
  "100 - Planner Corretora",
  "102 - XP Investimentos",
  "104 - Caixa",
  "107 - Banco BOCOM BBM",
  "113 - Banco Arbi",
  "119 - Banco Western Union",
  "121 - Agibank",
  "124 - Banco Woori",
  "136 - Uniprime",
  "138 - Getnet",
  "197 - Stone",
  "208 - BTG Pactual",
  "212 - Banco Original",
  "218 - Banco BS2",
  "222 - Banco Credit Agricole",
  "237 - Bradesco",
  "246 - ABC Brasil",
  "254 - Paraná Banco",
  "260 - Nubank",
  "265 - Banco Fator",
  "290 - PagBank",
  "318 - BMG",
  "323 - Mercado Pago",
  "335 - Banco Digio",
  "336 - C6 Bank",
  "341 - Itaú",
  "364 - Gerencianet (Efí)",
  "380 - PicPay",
  "383 - Juno",
  "399 - HSBC Brasil",
  "422 - Safra",
  "456 - Banco MUFG",
  "464 - Banco Sumitomo Mitsui",
  "473 - Banco Caixa Geral",
  "611 - Banco Paulista",
  "612 - Banco Guanabara",
  "623 - Banco Pan",
  "630 - Banco Smartbank",
  "654 - Neon",
  "735 - Neon Pagamentos",
  "745 - Citibank",
  "746 - Banco Modal",
  "748 - Sicredi",
  "752 - Banco BNP Paribas",
  "756 - Sicoob",
  "757 - Banco KEB Hana",
  "Outro"
]

TIPOS_CHAVE_PIX = ["CPF", "Celular", "E-mail", "CNPJ", "Chave Aleatória"]
TIPOS_CONTA = ["Corrente", "Poupança", "Pagamento", "Salário"]

# Opções Exatas Pedidas
SUBS_CLT = [
    "Margem Livre", 
    "Sem Margem", 
    "Não Elegível", 
    "Data Termino"
]

SUBS_INSS = [
    "Margem Livre", 
    "Sem Margem", 
    "Bloqueado", 
    "Tem Port", 
    "Sem Port", 
    "Tem Refin", 
    "Sem Refin"
]

SUBS_FGTS = [
    "Tem Saldo", 
    "Sem Saldo", 
    "Aniversário", 
    "Antecipação Feita"
]

# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================
def buscar_endereco_cep(cep):
    cep = str(cep).replace("-", "").replace(".", "").strip()
    if len(cep) == 8:
        try:
            r = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
            d = r.json()
            if "erro" not in d: return d
        except: return None
    return None

def card_stats_react(titulo, valor, subtitulo, cor_tema, icone):
    bg_icon = "#f1f5f9"; text_icon = "#475569"
    if cor_tema == "violet": bg_icon = "#f3e8ff"; text_icon = "#7c3aed"
    elif cor_tema == "green": bg_icon = "#dcfce7"; text_icon = "#16a34a"
    elif cor_tema == "blue": bg_icon = "#dbeafe"; text_icon = "#2563eb"
    elif cor_tema == "amber": bg_icon = "#ffedd5"; text_icon = "#ea580c"
    elif cor_tema == "red": bg_icon = "#fee2e2"; text_icon = "#dc2626"

    st.markdown(f"""
    <div class="react-card" style="display: flex; justify-content: space-between; align-items: start;">
        <div>
            <p style="color: #64748b; font-size: 13px; font-weight: 500; text-transform: uppercase; margin: 0;">{titulo}</p>
            <h3 style="color: #0f172a; font-size: 32px; font-weight: 700; margin: 4px 0 0 0; letter-spacing: -0.02em;">{valor}</h3>
            <p style="color: #94a3b8; font-size: 13px; margin: 4px 0 0 0;">{subtitulo}</p>
        </div>
        <div style="width: 48px; height: 48px; background-color: {bg_icon}; color: {text_icon}; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px;">
            {icone}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# RENDERIZAÇÃO DA PÁGINA
# ==========================================
def render_page(pagina_atual):
    
    # --- 1. LIMPEZA AUTOMÁTICA DE CAMPOS ---
    if st.session_state.get('limpar_formulario_cadastro', False):
        keys_to_clear = [
            'cad_nome', 'cad_cpf', 'cad_tipo', 'cad_tel', 'cad_sub', 
            'cad_cep', 'cad_rua', 'cad_num', 'cad_bairro', 'cad_cid', 'cad_uf', 'cad_mae',
            'cad_nasc', 'cad_termino', 'cad_consulta', 'cad_obs'
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        st.session_state.temp_lists = {'cad_pix':[], 'cad_bank':[], 'ed_pix':[], 'ed_bank':[]}
        st.session_state['limpar_formulario_cadastro'] = False

    # Inicializa variáveis padrão se não existirem
    for k in ['cad_rua', 'cad_bairro', 'cad_cid', 'cad_uf', 'cad_num']:
        if k not in st.session_state: st.session_state[k] = ""
    if 'temp_lists' not in st.session_state: st.session_state.temp_lists = {'cad_pix':[], 'cad_bank':[], 'ed_pix':[], 'ed_bank':[]}
    if 'edit_pix_list' not in st.session_state: st.session_state.edit_pix_list = []
    if 'edit_bank_list' not in st.session_state: st.session_state.edit_bank_list = []

    # --- FILTRO USUÁRIO ---
    filtro_usuario = st.session_state.username 
    if st.session_state.role == 'admin':
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Filtro Admin**")
        lista_users = ["Todos"] + db.get_lista_nomes_usuarios()
        filtro_usuario = st.sidebar.selectbox("Ver dados de:", lista_users)
    
    df = db.get_clientes(filtro_usuario)
    
    # Cabeçalho
    if pagina_atual == "Dashboard":
        st.markdown(f"## Olá, {st.session_state.username}")
        st.markdown("<p style='color: #64748b;'>Visão geral da sua carteira hoje.</p>", unsafe_allow_html=True)
    elif pagina_atual == "Clientes":
        st.markdown("## Carteira de Clientes")
    elif pagina_atual == "Novo Cadastro":
        st.markdown("## Novo Cadastro")

    st.write("") 

    # ==========================
    # DASHBOARD (LÓGICA DE ALERTAS)
    # ==========================
    if pagina_atual == "Dashboard":
        total = len(df)
        pendentes = len(df[df['status_venda'] == 'Pendente'])
        
        # Conta Bloqueados/Não Elegíveis para estatística
        bloqueados = len(df[df['status_venda'].isin(['Não Elegível', 'Bloqueado'])])
        
        hoje = datetime.now().date()
        dia_semana = hoje.weekday() # 0=Seg, 1=Ter, ..., 6=Dom
        dia_mes = hoje.day

        tarefas = []

        # Loop em todos os clientes para verificar regras
        for idx, row in df.iterrows():
            nome = row['nome']
            tipo = row['tipo']
            sub = row['sub_categoria'] # Situação
            
            # Converter datas
            data_term = None
            if row.get('data_termino'):
                try: data_term = datetime.strptime(str(row['data_termino']), '%Y-%m-%d').date()
                except: pass
            
            data_cons = None
            if row.get('data_consulta'):
                try: data_cons = datetime.strptime(str(row['data_consulta']), '%Y-%m-%d').date()
                except: pass

            # -----------------------------------------------
            # REGRAS DE ALERTAS
            # -----------------------------------------------

            # 1. CLT
            if tipo == "CLT":
                # SE TIVER DATA TÉRMINO ATIVA, NÃO AVISA NADA (BLOQUEIO TOTAL)
                if data_term and data_term >= hoje:
                    continue # Pula este cliente, não gera alerta
                
                # Se não tiver data término ou já passou...
                if sub == "Não Elegível":
                    # Avisar toda Terça-feira (1)
                    if dia_semana == 1:
                        tarefas.append(f"🔎 Consultar CLT (Elegibilidade): {nome}")
                
                elif sub == "Margem Livre" and row['status_venda'] == "Pendente":
                    # Avisa todo dia se tem margem
                    tarefas.append(f"✅ Margem Livre CLT: {nome}")

            # 2. INSS
            elif tipo == "INSS":
                if sub == "Bloqueado":
                    # Avisar toda Terça-feira (1)
                    if dia_semana == 1:
                        tarefas.append(f"🔓 Tentar Desbloqueio INSS: {nome}")
                
                elif sub in ["Tem Port", "Tem Refin"]:
                    # Avisar todo dia
                    tarefas.append(f"💲 Oportunidade ({sub}): {nome}")
                
                elif sub == "Margem Livre" and row['status_venda'] == "Pendente":
                    tarefas.append(f"✅ Margem Livre INSS: {nome}")

            # 3. FGTS
            elif tipo == "FGTS":
                if sub == "Tem Saldo":
                    tarefas.append(f"💰 FGTS com Saldo: {nome}")
                
                elif sub == "Sem Saldo":
                    # Avisar dia 10 E dias 20 a 28
                    dias_aviso = [10, 20, 21, 22, 23, 24, 25, 26, 27, 28]
                    if dia_mes in dias_aviso:
                        tarefas.append(f"📅 Consultar Saldo FGTS: {nome}")
                
                elif sub == "Aniversário":
                    # Avisar na data específica
                    if data_cons and data_cons <= hoje and row['status_venda'] != "Fechado Comigo":
                        tarefas.append(f"🎂 Aniversário FGTS (Consultar): {nome}")

        # Renderizar Cards
        c1, c2, c3, c4 = st.columns(4)
        with c1: card_stats_react("Total Clientes", total, "Carteira ativa", "blue", "👥")
        with c2: card_stats_react("Pendentes", pendentes, "Em andamento", "amber", "⏳")
        with c3: card_stats_react("Bloqueados", bloqueados, "Monitorando", "red", "🚫")
        
        with c4: 
            msg = f"{len(tarefas)} Alertas" if tarefas else "Tudo limpo"
            cor_alerta = "violet" if len(tarefas) > 0 else "green"
            card_stats_react("Tarefas Hoje", len(tarefas), msg, cor_alerta, "🔔")

        st.write("")
        col_left, col_right = st.columns([2, 1])

        with col_left:
            st.markdown("### Clientes Recentes")
            st.markdown('<div class="react-card" style="padding: 0; overflow: hidden;">', unsafe_allow_html=True)
            st.markdown("""
            <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; padding: 12px 24px; background-color: #f8fafc; border-bottom: 1px solid #e2e8f0; color: #64748b; font-size: 12px; font-weight: 600; text-transform: uppercase;">
                <div>Cliente</div>
                <div>Situação</div>
                <div>Data</div>
                <div style="text-align: right;">Status</div>
            </div>
            """, unsafe_allow_html=True)

            if not df.empty:
                recentes = df.tail(6).iloc[::-1]
                for i, r in recentes.iterrows():
                    bg_st = "#f1f5f9"; cl_st = "#475569"
                    if "Pendente" in r['status_venda']: bg_st = "#fff7ed"; cl_st = "#c2410c"
                    if r['status_venda'] in ["Não Elegível", "Bloqueado"]: bg_st = "#fef2f2"; cl_st = "#991b1b"
                    if "Fechado" in r['status_venda']: bg_st = "#f0fdf4"; cl_st = "#15803d"

                    st.markdown(f"""
                    <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; padding: 16px 24px; border-bottom: 1px solid #f1f5f9; align-items: center;">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div style="width: 32px; height: 32px; border-radius: 50%; background: #f1f5f9; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; color: #64748b;">
                                {r['nome'][0] if r['nome'] else '?'}
                            </div>
                            <div>
                                <div style="font-weight: 500; color: #0f172a; font-size: 14px;">{r['nome']}</div>
                                <div style="color: #94a3b8; font-size: 12px;">{r['tipo']}</div>
                            </div>
                        </div>
                        <div style="color: #64748b; font-size: 13px;">{r['sub_categoria']}</div>
                        <div style="color: #64748b; font-size: 13px;">{r['criado_em']}</div>
                        <div style="text-align: right;">
                            <span style="background: {bg_st}; color: {cl_st}; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 600;">{r['status_venda']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("<div style='padding: 24px; text-align: center; color: #94a3b8;'>Nenhum dado.</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_right:
            st.markdown("### Lembretes do Dia")
            st.markdown('<div class="react-card" style="max-height: 400px; overflow-y: auto;">', unsafe_allow_html=True)
            if tarefas:
                for t in tarefas:
                    st.markdown(f"""
                    <div style="margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid #f1f5f9;">
                        <div style="font-size: 14px; font-weight: 600; color: #475569;">{t}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("<p style='color: #94a3b8; text-align: center; margin-top: 20px;'>Nenhuma pendência hoje! 🎉</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ==========================
    # NOVO CADASTRO
    # ==========================
    elif pagina_atual == "Novo Cadastro":
        with st.container():
            st.markdown('<div class="react-card">', unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                nn = st.text_input("Nome Completo", key="cad_nome")
                nc = st.text_input("CPF", key="cad_cpf")
                
                # TIPO (Isso define o que aparece no próximo dropdown)
                nt = st.selectbox("Tipo", ["CLT", "INSS", "FGTS"], key="cad_tipo")
                
                # Formato DD/MM/YYYY
                nas = st.date_input("Nascimento", min_value=date(1920, 1, 1), max_value=date(2030, 12, 31), key="cad_nasc", format="DD/MM/YYYY")
            
            with c2:
                ntel = st.text_input("Telefone", key="cad_tel")
                
                # --- DEFINIÇÃO DINÂMICA DAS OPÇÕES DE SITUAÇÃO ---
                if nt == "INSS": 
                    opcoes_sub = SUBS_INSS
                elif nt == "FGTS": 
                    opcoes_sub = SUBS_FGTS
                else: 
                    opcoes_sub = SUBS_CLT # CLT é o padrão
                
                nsub = st.selectbox("Situação", opcoes_sub, key="cad_sub")

                # Campos Condicionais de Data
                data_termino = None
                data_consulta = None

                if nt == "CLT":
                    st.caption("Contrato de Trabalho")
                    data_termino = st.date_input("Data de Término (Opcional)", value=None, key="cad_termino", help="Preencha se o contrato tiver fim determinado.", format="DD/MM/YYYY")
                
                if nt == "FGTS" and nsub == "Aniversário":
                    st.caption("Programar Consulta")
                    data_consulta = st.date_input("Data para Consultar", value=None, key="cad_consulta", help="Data que o sistema emitirá o alerta.", format="DD/MM/YYYY")

            # --- BUSCA CEP MAIS BONITA E ALINHADA ---
            st.markdown("---")
            
            # Layout de Colunas Ajustado: [CEP Input] [Botão Buscar] [Vazio]
            col_cep_layout = st.columns([0.3, 0.2, 0.5]) 
            
            with col_cep_layout[0]:
                ncep = st.text_input("CEP", key="cad_cep", placeholder="00000-000")
                
            with col_cep_layout[1]:
                # Espaçador para alinhar o botão com o input (compensa o label do input)
                st.markdown("<div style='height: 29px;'></div>", unsafe_allow_html=True)
                # Botão 'secondary' é mais clean (fundo branco com borda) e ícone
                if st.button("🔍 Buscar", key="btn_busca_cep_cad", use_container_width=True, type="secondary"):
                    d = buscar_endereco_cep(ncep)
                    if d:
                        st.session_state.cad_rua = d.get('logradouro', '')
                        st.session_state.cad_bairro = d.get('bairro', '')
                        st.session_state.cad_cid = d.get('localidade', '')
                        st.session_state.cad_uf = d.get('uf', '')
                        st.toast("Endereço encontrado!", icon="✅")
                        st.rerun()
                    else: st.error("CEP inválido")

            e1, e2 = st.columns([3, 1])
            nrua = e1.text_input("Endereço", key="cad_rua")
            nnum = e2.text_input("Número", key="cad_num")
            e3, e4, e5 = st.columns(3)
            nbai = e3.text_input("Bairro", key="cad_bairro")
            ncid = e4.text_input("Cidade", key="cad_cid")
            nuf = e5.text_input("UF", key="cad_uf")
            nmae = st.text_input("Nome da Mãe", key="cad_mae")

            st.markdown("---")
            st.caption("Financeiro")
            
            f1, f2 = st.columns(2)
            with f1:
                tpix = st.selectbox("Tipo Pix", TIPOS_CHAVE_PIX)
                cpix = st.text_input("Chave Pix")
                if st.button("Adicionar Pix"):
                    st.session_state.temp_lists['cad_pix'].append(f"{tpix}: {cpix}")
                for p in st.session_state.temp_lists['cad_pix']: st.markdown(f"🔹 {p}")
            
            with f2:
                bn = st.selectbox("Banco", LISTA_BANCOS)
                b_ag = st.text_input("Agência")
                b_cc = st.text_input("Conta")
                b_tipo = st.selectbox("Tipo Conta", TIPOS_CONTA)
                if st.button("Adicionar Conta"):
                    st.session_state.temp_lists['cad_bank'].append(f"{bn} | Ag: {b_ag} | Cc: {b_cc} ({b_tipo})")
                for b in st.session_state.temp_lists['cad_bank']: st.markdown(f"🏦 {b}")

            obs = st.text_area("Observações", key="cad_obs")
            
            st.write("")
            if st.button("SALVAR CADASTRO", use_container_width=True, type="primary"):
                # Status Automático
                status_inicial = "Pendente"
                if nsub == "Não Elegível": status_inicial = "Não Elegível"
                if nsub == "Bloqueado": status_inicial = "Bloqueado"
                if nsub == "Sem Margem": status_inicial = "Pendente" # Ou outra lógica se preferir
                
                dados = {
                    "nome": nn, "telefone": ntel, "cpf": nc, "tipo": nt, "sub_categoria": nsub,
                    "status_venda": status_inicial, "data_nascimento": nas, "notas": obs,
                    "cep": ncep, "endereco": nrua, "numero": nnum, "bairro": nbai, "cidade": ncid, "estado": nuf, "nome_mae": nmae,
                    "pix_chave": " | ".join(st.session_state.temp_lists['cad_pix']),
                    "dados_bancarios": " || ".join(st.session_state.temp_lists['cad_bank']),
                    "usuario_responsavel": st.session_state.username,
                    "data_termino": data_termino if data_termino else "",
                    "data_consulta": data_consulta if data_consulta else ""
                }
                db.add_cliente(dados)
                st.success("Salvo com sucesso!")
                st.session_state['limpar_formulario_cadastro'] = True
                time.sleep(1); st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

    # ==========================
    # CLIENTES / EDIÇÃO
    # ==========================
    elif pagina_atual == "Clientes":
        c_filtros = st.columns([2, 1, 1])
        filter_text = c_filtros[0].text_input("Buscar", placeholder="Nome ou CPF...")
        f_tipo = c_filtros[1].multiselect("Tipo", df['tipo'].unique() if not df.empty else [])
        f_status = c_filtros[2].multiselect("Status", df['status_venda'].unique() if not df.empty else [])
        
        df_show = df.copy()
        if f_tipo: df_show = df_show[df_show['tipo'].isin(f_tipo)]
        if f_status: df_show = df_show[df_show['status_venda'].isin(f_status)]
        if filter_text: df_show = df_show[df_show['nome'].astype(str).str.contains(filter_text, case=False)]
        
        st.dataframe(df_show, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("### Editar Cliente")
        
        sel_cli = st.selectbox("Selecione:", ["Selecione"] + df['nome'].tolist())
        
        if sel_cli != "Selecione":
            row = df[df['nome'] == sel_cli].iloc[0]
            id_sel = row['id']
            
            st.markdown('<div class="react-card">', unsafe_allow_html=True)
            
            ec1, ec2 = st.columns(2)
            enome = ec1.text_input("Nome", value=row['nome'])
            ecpf = ec2.text_input("CPF", value=str(row['cpf']))
            
            ec3, ec4 = st.columns(2)
            etipo = ec3.selectbox("Tipo", ["CLT", "INSS", "FGTS"], index=["CLT", "INSS", "FGTS"].index(row['tipo']) if row['tipo'] in ["CLT", "INSS", "FGTS"] else 0)
            
            # --- LISTAS DINÂMICAS NA EDIÇÃO ---
            if etipo == "INSS": opcoes_sub_ed = SUBS_INSS
            elif etipo == "FGTS": opcoes_sub_ed = SUBS_FGTS
            else: opcoes_sub_ed = SUBS_CLT
            
            idx_sub = 0
            if row['sub_categoria'] in opcoes_sub_ed: idx_sub = opcoes_sub_ed.index(row['sub_categoria'])
            esub = ec3.selectbox("Situação", opcoes_sub_ed, index=idx_sub)
            
            # Status
            lista_status = ["Pendente", "Não Elegível", "Bloqueado", "Fechado Comigo", "Fechado com Outro", "Sem Interesse"]
            idx_st = 0
            if row['status_venda'] in lista_status: idx_st = lista_status.index(row['status_venda'])
            estat = ec4.selectbox("Status", lista_status, index=idx_st)

            # Datas Extras
            edata_term = None
            if etipo == "CLT":
                val_dt = None
                if row.get('data_termino'):
                    try: val_dt = datetime.strptime(str(row['data_termino']), '%Y-%m-%d').date()
                    except: pass
                edata_term = ec4.date_input("Data Término", value=val_dt, format="DD/MM/YYYY")

            edata_cons = None
            if etipo == "FGTS" and esub == "Aniversário":
                val_dc = None
                if row.get('data_consulta'):
                    try: val_dc = datetime.strptime(str(row['data_consulta']), '%Y-%m-%d').date()
                    except: pass
                edata_cons = ec4.date_input("Data Consulta", value=val_dc, format="DD/MM/YYYY")

            # --- BUSCA CEP NA EDIÇÃO (Também melhorada) ---
            st.markdown("#### Endereço & Contato")
            
            col_ed_cep_layout = st.columns([0.3, 0.2, 0.5])
            with col_ed_cep_layout[0]:
                ecep = st.text_input("CEP", value=str(row['cep']), key="e_cep_in")
            with col_ed_cep_layout[1]:
                st.markdown("<div style='height: 29px;'></div>", unsafe_allow_html=True)
                if st.button("🔍 Buscar", key="btn_e_cep", use_container_width=True, type="secondary"):
                    d = buscar_endereco_cep(ecep)
                    if d:
                        st.session_state.ed_end = d.get('logradouro','')
                        st.session_state.ed_bai = d.get('bairro','')
                        st.session_state.ed_cid = d.get('localidade','')
                        st.session_state.ed_uf = d.get('uf','')
                        st.toast("Endereço Atualizado.")
                        st.rerun()
            
            val_end = st.session_state.ed_end if st.session_state.ed_end else str(row['endereco'])
            val_bai = st.session_state.ed_bai if st.session_state.ed_bai else str(row['bairro'])
            val_cid = st.session_state.ed_cid if st.session_state.ed_cid else str(row['cidade'])
            val_uf = st.session_state.ed_uf if st.session_state.ed_uf else str(row['estado'])

            ee1, ee2 = st.columns(2)
            eend = ee1.text_input("Endereço", value=val_end)
            enum = ee2.text_input("Número", value=str(row['numero']))
            ee3, ee4 = st.columns(2)
            ebai = ee3.text_input("Bairro", value=val_bai)
            emae = ee4.text_input("Mãe", value=str(row['nome_mae']))

            enota = st.text_area("Notas", value=row['notas'])
            
            c_up, c_del = st.columns([4, 1])
            if c_up.button("ATUALIZAR DADOS", type="primary"):
                db.update_cliente_completo(id_sel, {
                    "nome": enome, "cpf": ecpf, "tipo": etipo, "sub_categoria": esub, "status_venda": estat, 
                    "cep": ecep, "endereco": eend, "numero": enum, "bairro": ebai, "cidade": val_cid, "estado": val_uf, "nome_mae": emae,
                    "notas": enota,
                    "data_termino": edata_term if edata_term else "",
                    "data_consulta": edata_cons if edata_cons else ""
                })
                st.session_state.ed_end = ""
                st.session_state.ed_bai = ""
                st.session_state.ed_cid = ""
                st.session_state.ed_uf = ""
                st.success("Salvo!"); time.sleep(1); st.rerun()
            
            if c_del.button("🗑️"):
                db.delete_cliente(id_sel); st.success("Deletado!"); time.sleep(1); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
