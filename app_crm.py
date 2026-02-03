import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import time
import database as db 

# --- Helpers ---
LISTA_BANCOS = ["001 - Banco do Brasil", "033 - Santander", "104 - Caixa", "237 - Bradesco", "341 - Itaú", "260 - Nubank", "077 - Inter", "Outro"]
TIPOS_CHAVE_PIX = ["CPF", "Celular", "E-mail", "CNPJ", "Chave Aleatória"]

def buscar_endereco_cep(cep):
    cep = str(cep).replace("-", "").replace(".", "").strip()
    if len(cep) == 8:
        try:
            r = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
            d = r.json()
            if "erro" not in d: return d
        except: return None
    return None

def card_stats_moderno(titulo, valor, subtitulo, cor_icone, icone_emoji):
    """
    Cria um card estilo React/Tailwind
    """
    bg_icon = ""
    text_icon = ""
    
    # Define cores baseadas no tema violeta/roxo
    if cor_icone == "roxo":
        bg_icon = "#f3e8ff" # purple-100
        text_icon = "#7e22ce" # purple-700
    elif cor_icone == "verde":
        bg_icon = "#dcfce7" # green-100
        text_icon = "#15803d" # green-700
    elif cor_icone == "azul":
        bg_icon = "#dbeafe" # blue-100
        text_icon = "#1d4ed8" # blue-700
    else:
        bg_icon = "#f1f5f9"
        text_icon = "#475569"

    st.markdown(f"""
    <div class="dashboard-card" style="display: flex; align-items: start; justify-content: space-between; height: 100%;">
        <div>
            <p style="color: #64748b; font-size: 13px; font-weight: 500; margin: 0; text-transform: uppercase; letter-spacing: 0.5px;">{titulo}</p>
            <h3 style="color: #0f172a; font-size: 28px; font-weight: 700; margin: 4px 0 0 0;">{valor}</h3>
            <p style="color: #94a3b8; font-size: 12px; margin: 4px 0 0 0;">{subtitulo}</p>
        </div>
        <div style="background-color: {bg_icon}; color: {text_icon}; width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px;">
            {icone_emoji}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_crm():
    # Inicializa Vars
    vars_ed = ['ed_nome', 'ed_cpf', 'ed_tel', 'ed_tipo', 'ed_sub', 'ed_stat', 'ed_cep', 'ed_end', 'ed_num', 'ed_bai', 'ed_cid', 'ed_uf', 'ed_mae', 'ed_pix_str', 'ed_bank_str', 'ed_nota']
    for v in vars_ed:
        if v not in st.session_state: st.session_state[v] = ""
    if 'ed_nasc' not in st.session_state: st.session_state.ed_nasc = None
    if 'temp_lists' not in st.session_state: st.session_state.temp_lists = {'cad_pix':[], 'cad_bank':[], 'ed_pix':[], 'ed_bank':[]}

    filtro_usuario = st.session_state.username 
    if st.session_state.role == 'admin':
        st.sidebar.markdown("### 👁️ Filtro")
        lista_users = ["Todos"] + db.get_lista_nomes_usuarios()
        filtro_usuario = st.sidebar.selectbox("Carteira:", lista_users)
    
    df = db.get_clientes(filtro_usuario)
    
    # Menu Superior estilo abas
    menu = st.radio("", ["Dashboard", "Clientes", "Novo Cadastro"], horizontal=True, label_visibility="collapsed")
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # ==========================
    # DASHBOARD (VISUAL TXT)
    # ==========================
    if menu == "Dashboard":
        st.markdown(f"## Olá, {st.session_state.username}")
        st.markdown("<p style='color: #64748b;'>Aqui está o resumo da sua operação hoje.</p>", unsafe_allow_html=True)
        st.write("")

        total = len(df)
        pendentes = len(df[df['status_venda'] == 'Pendente'])
        fechados = len(df[df['status_venda'].str.contains('Fechado', na=False)])
        hoje_num = len(df[df['criado_em'] == str(datetime.now().date())])

        # Grid de Cards
        c1, c2, c3, c4 = st.columns(4)
        with c1: card_stats_moderno("Total Clientes", total, "Base completa", "azul", "👥")
        with c2: card_stats_moderno("Pendentes", pendentes, "Aguardando ação", "roxo", "⏳")
        with c3: card_stats_moderno("Fechados", fechados, "Contratos finalizados", "verde", "✅")
        with c4: card_stats_moderno("Hoje", hoje_num, "Novos cadastros", "azul", "📅")

        st.write("")
        st.write("")

        col_left, col_right = st.columns([2, 1])

        # Lista de Clientes Recentes (Estilo Tabela Clean)
        with col_left:
            st.markdown("### Clientes Recentes")
            st.markdown('<div class="dashboard-card" style="padding: 0; overflow: hidden;">', unsafe_allow_html=True)
            
            # Cabeçalho da tabela fake
            st.markdown("""
            <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; padding: 12px 24px; background-color: #f8fafc; border-bottom: 1px solid #e2e8f0; color: #64748b; font-size: 12px; font-weight: 600; text-transform: uppercase;">
                <div>Cliente</div>
                <div>Tipo</div>
                <div>Data</div>
                <div style="text-align: right;">Status</div>
            </div>
            """, unsafe_allow_html=True)

            if not df.empty:
                recentes = df.tail(6).iloc[::-1]
                for i, r in recentes.iterrows():
                    # Status colorido
                    status_style = "background:#f1f5f9; color:#475569;"
                    if "Pendente" in r['status_venda']: status_style = "background:#fff7ed; color:#c2410c;"
                    if "Fechado" in r['status_venda']: status_style = "background:#f0fdf4; color:#15803d;"

                    st.markdown(f"""
                    <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; padding: 16px 24px; border-bottom: 1px solid #f1f5f9; align-items: center;">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div style="width: 32px; height: 32px; border-radius: 50%; background: #f1f5f9; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; color: #64748b;">
                                {r['nome'][0] if r['nome'] else '?'}
                            </div>
                            <div>
                                <div style="font-weight: 500; color: #0f172a; font-size: 14px;">{r['nome']}</div>
                                <div style="color: #94a3b8; font-size: 12px;">{r['telefone']}</div>
                            </div>
                        </div>
                        <div style="color: #64748b; font-size: 14px;">{r['tipo']}</div>
                        <div style="color: #64748b; font-size: 14px;">{r['criado_em']}</div>
                        <div style="text-align: right;">
                            <span style="{status_style} padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600;">{r['status_venda']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("<div style='padding: 24px; text-align: center; color: #94a3b8;'>Nenhum dado.</div>", unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

        # Lembretes (Estilo Lista Lateral)
        with col_right:
            st.markdown("### Lembretes do Dia")
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            
            hoje = datetime.now().date()
            lembretes = []
            
            # Lógica simplificada de lembretes
            if hoje.day in [10, 20, 26]:
                qtd = len(df[(df['tipo']=='FGTS') & (df['sub_categoria'].isin(['Sem Saldo', 'Antecipação Feita']))])
                if qtd > 0: lembretes.append({"msg": f"FGTS: {qtd} clientes sem saldo", "cor": "#f59e0b"})
            
            def chk_niver(d):
                try: x=pd.to_datetime(d); return x.day==hoje.day and x.month==hoje.month
                except: return False
            qtd_niver = len(df[df['data_nascimento'].apply(chk_niver)])
            if qtd_niver > 0: lembretes.append({"msg": f"Aniversários: {qtd_niver} hoje", "cor": "#ec4899"})

            if lembretes:
                for L in lembretes:
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
                        <div style="width: 8px; height: 8px; border-radius: 50%; background-color: {L['cor']};"></div>
                        <div style="font-size: 14px; color: #334155; font-weight: 500;">{L['msg']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("<p style='color: #94a3b8; font-size: 14px;'>Tudo limpo por hoje!</p>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

    # ==========================
    # NOVO CADASTRO
    # ==========================
    elif menu == "Novo Cadastro":
        st.markdown("### Novo Cliente")
        with st.container():
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                nn = st.text_input("Nome Completo", key="cad_nome")
                nc = st.text_input("CPF", key="cad_cpf")
                nt = st.selectbox("Tipo", ["INSS", "CLT", "FGTS"], key="cad_tipo")
                nas = st.date_input("Nascimento", min_value=date(1920, 1, 1), max_value=date(2030, 12, 31))
            with c2:
                ntel = st.text_input("Telefone", key="cad_tel")
                nsub = st.selectbox("Situação", ["Margem Livre", "Sem Margem", "Tem Saldo", "Sem Saldo", "Antecipação Feita"], key="cad_sub")
                ncep = st.text_input("CEP", key="cad_cep")
                if st.button("Buscar CEP"):
                    d = buscar_endereco_cep(ncep)
                    if d: st.toast("Endereço preenchido")
            
            st.markdown("---")
            st.caption("Financeiro")
            f1, f2 = st.columns(2)
            with f1:
                tpix = st.selectbox("Tipo Pix", TIPOS_CHAVE_PIX)
                cpix = st.text_input("Chave Pix")
                if st.button("Adicionar Pix"):
                    st.session_state.temp_lists['cad_pix'].append(f"{tpix}: {cpix}")
                for p in st.session_state.temp_lists['cad_pix']: st.markdown(f"• {p}")
            
            with f2:
                bn = st.selectbox("Banco", LISTA_BANCOS)
                bcc = st.text_input("Conta")
                if st.button("Adicionar Conta"):
                    st.session_state.temp_lists['cad_bank'].append(f"{bn} Cc:{bcc}")
                for b in st.session_state.temp_lists['cad_bank']: st.markdown(f"• {b}")

            obs = st.text_area("Observações")
            
            st.write("")
            if st.button("SALVAR CADASTRO", type="primary", use_container_width=True):
                dados = {
                    "nome": nn, "telefone": ntel, "cpf": nc, "tipo": nt, "sub_categoria": nsub,
                    "status_venda": "Pendente", "data_nascimento": nas, "notas": obs, "cep": ncep,
                    "pix_chave": " | ".join(st.session_state.temp_lists['cad_pix']),
                    "dados_bancarios": " || ".join(st.session_state.temp_lists['cad_bank']),
                    "usuario_responsavel": st.session_state.username
                }
                db.add_cliente(dados)
                st.success("Salvo!")
                st.session_state.temp_lists['cad_pix'] = []
                st.session_state.temp_lists['cad_bank'] = []
            
            st.markdown('</div>', unsafe_allow_html=True)

    # ==========================
    # LISTA
    # ==========================
    elif menu == "Clientes":
        st.markdown(f"### Carteira de Clientes")
        
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
        st.markdown("### Editar")
        
        sel_cli = st.selectbox("Selecione:", ["Selecione"] + df['nome'].tolist())
        
        if sel_cli != "Selecione":
            row = df[df['nome'] == sel_cli].iloc[0]
            id_sel = row['id']
            
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            ec1, ec2 = st.columns(2)
            enome = ec1.text_input("Nome", value=row['nome'])
            estat = ec2.selectbox("Status", ["Pendente", "Fechado Comigo", "Fechado com Outro", "Sem Interesse"], index=0)
            enota = st.text_area("Notas", value=row['notas'])
            
            c_up, c_del = st.columns([4, 1])
            if c_up.button("Atualizar", type="primary"):
                db.update_cliente_completo(id_sel, {"nome": enome, "status_venda": estat, "notas": enota})
                st.success("Salvo!"); time.sleep(1); st.rerun()
            
            if c_del.button("🗑️"):
                db.delete_cliente(id_sel); st.success("Deletado!"); time.sleep(1); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)