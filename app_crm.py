import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import time
import database as db 

# --- Helpers e Listas ---
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

def card_dashboard(titulo, valor, icone, cor_bg_icone, cor_texto_icone):
    st.markdown(f"""
    <div class="custom-card" style="padding: 20px; display: flex; align-items: center; justify-content: space-between;">
        <div>
            <div style="color: #64748b; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">{titulo}</div>
            <div style="color: #1e293b; font-size: 28px; font-weight: 700; margin-top: 5px;">{valor}</div>
        </div>
        <div style="width: 48px; height: 48px; background-color: {cor_bg_icone}; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: {cor_texto_icone}; font-size: 20px;">
            {icone}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_crm():
    # Inicializa variáveis
    vars_ed = ['ed_nome', 'ed_cpf', 'ed_tel', 'ed_tipo', 'ed_sub', 'ed_stat', 'ed_cep', 'ed_end', 'ed_num', 'ed_bai', 'ed_cid', 'ed_uf', 'ed_mae', 'ed_pix_str', 'ed_bank_str', 'ed_nota']
    for v in vars_ed:
        if v not in st.session_state: st.session_state[v] = ""
    if 'ed_nasc' not in st.session_state: st.session_state.ed_nasc = None
    if 'temp_lists' not in st.session_state: st.session_state.temp_lists = {'cad_pix':[], 'cad_bank':[], 'ed_pix':[], 'ed_bank':[]}

    filtro_usuario = st.session_state.username 
    if st.session_state.role == 'admin':
        st.sidebar.markdown("### 👁️ Filtro Admin")
        lista_users = ["Todos"] + db.get_lista_nomes_usuarios()
        filtro_usuario = st.sidebar.selectbox("Ver dados de:", lista_users)
    
    df = db.get_clientes(filtro_usuario)
    
    # Navegação com estilo de abas superiores
    menu = st.radio("Navegação", ["Dashboard", "Clientes", "Novo Cadastro"], horizontal=True, label_visibility="collapsed")
    st.write("")

    # ==========================
    # DASHBOARD
    # ==========================
    if menu == "Dashboard":
        st.markdown(f"## Olá, <span style='color: #7c3aed'>{st.session_state.username}</span>! 👋", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748b; margin-top: -10px;'>Aqui está o resumo da sua carteira hoje.</p>", unsafe_allow_html=True)
        st.write("")

        # Métricas
        total = len(df)
        pendentes = len(df[df['status_venda'] == 'Pendente'])
        fechados = len(df[df['status_venda'].str.contains('Fechado', na=False)])
        
        c1, c2, c3 = st.columns(3)
        with c1: card_dashboard("Total Clientes", total, "👥", "#eff6ff", "#3b82f6") # Azul
        with c2: card_dashboard("Pendentes", pendentes, "⏳", "#fff7ed", "#f97316") # Laranja
        with c3: card_dashboard("Fechados", fechados, "✅", "#f0fdf4", "#22c55e") # Verde

        st.write("")
        col_main, col_side = st.columns([2, 1])

        with col_main:
            st.markdown("### 📋 Clientes Recentes")
            if not df.empty:
                recentes = df.tail(5).iloc[::-1]
                for i, r in recentes.iterrows():
                    # Estilo da Badge de Status
                    bg_status = "#f3f4f6"; color_status = "#4b5563"
                    if "Pendente" in r['status_venda']: bg_status = "#fff7ed"; color_status = "#c2410c"
                    elif "Fechado" in r['status_venda']: bg_status = "#f0fdf4"; color_status = "#15803d"
                    
                    st.markdown(f"""
                    <div style="background: white; padding: 16px; border-radius: 12px; margin-bottom: 10px; border: 1px solid #f1f5f9; display: flex; align-items: center; justify-content: space-between;">
                        <div style="display: flex; align-items: center; gap: 15px;">
                            <div style="width: 40px; height: 40px; border-radius: 50%; background: #f8fafc; display: flex; align-items: center; justify-content: center; font-weight: 700; color: #64748b;">
                                {r['nome'][0].upper() if r['nome'] else '?'}
                            </div>
                            <div>
                                <div style="font-weight: 600; color: #334155;">{r['nome']}</div>
                                <div style="font-size: 12px; color: #94a3b8;">{r['tipo']} • {r['telefone']}</div>
                            </div>
                        </div>
                        <div style="background: {bg_status}; color: {color_status}; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">
                            {r['status_venda']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Nenhum cliente.")

        with col_side:
            st.markdown("### 📅 Lembretes")
            st.markdown('<div class="custom-card" style="padding: 20px;">', unsafe_allow_html=True)
            
            hoje = datetime.now().date()
            tem_aviso = False
            
            # Aniversariantes
            def check_niver(d_str):
                try: d = pd.to_datetime(d_str); return d.day == hoje.day and d.month == hoje.month
                except: return False
            niver = df[df['data_nascimento'].apply(check_niver)]
            if not niver.empty:
                st.markdown(f"**🎂 {len(niver)} Aniversariantes**")
                tem_aviso = True

            # FGTS (Dia 10 ou 20-28)
            if hoje.day == 10 or (20 <= hoje.day <= 28):
                fgts = df[(df['tipo']=='FGTS') & (df['sub_categoria'].isin(['Sem Saldo', 'Antecipação Feita']))]
                if not fgts.empty:
                    st.markdown(f"**💰 {len(fgts)} FGTS para rever**")
                    tem_aviso = True
            
            if not tem_aviso:
                st.caption("Nenhum lembrete urgente hoje.")
            
            st.markdown('</div>', unsafe_allow_html=True)

    # ==========================
    # NOVO CADASTRO
    # ==========================
    elif menu == "Novo Cadastro":
        st.markdown("### 📝 Novo Cliente")
        with st.container():
            # Container estilizado pelo CSS custom-card
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            
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
                if st.button("Buscar Endereço"):
                    d = buscar_endereco_cep(ncep)
                    if d: st.toast("Endereço carregado!")
            
            st.markdown("---")
            st.caption("Dados Financeiros")
            f1, f2 = st.columns(2)
            with f1:
                tpix = st.selectbox("Tipo Pix", TIPOS_CHAVE_PIX)
                cpix = st.text_input("Chave Pix")
                if st.button("Adicionar Pix"):
                    st.session_state.temp_lists['cad_pix'].append(f"{tpix}: {cpix}")
                for p in st.session_state.temp_lists['cad_pix']: st.markdown(f"- {p}")
            
            with f2:
                bn = st.selectbox("Banco", LISTA_BANCOS)
                bcc = st.text_input("Conta")
                if st.button("Adicionar Banco"):
                    st.session_state.temp_lists['cad_bank'].append(f"{bn} Cc:{bcc}")
                for b in st.session_state.temp_lists['cad_bank']: st.markdown(f"- {b}")

            obs = st.text_area("Observações")
            
            st.write("")
            if st.button("💾 SALVAR CADASTRO", type="primary", use_container_width=True):
                dados = {
                    "nome": nn, "telefone": ntel, "cpf": nc, "tipo": nt, "sub_categoria": nsub,
                    "status_venda": "Pendente", "data_nascimento": nas, "notas": obs,
                    "cep": ncep, "pix_chave": " | ".join(st.session_state.temp_lists['cad_pix']),
                    "dados_bancarios": " || ".join(st.session_state.temp_lists['cad_bank']),
                    "usuario_responsavel": st.session_state.username
                }
                db.add_cliente(dados)
                st.success("Cliente cadastrado com sucesso!")
                st.session_state.temp_lists['cad_pix'] = []
                st.session_state.temp_lists['cad_bank'] = []
            
            st.markdown('</div>', unsafe_allow_html=True)

    # ==========================
    # LISTA DE CLIENTES
    # ==========================
    elif menu == "Clientes":
        st.markdown(f"### 👥 Todos os Clientes ({len(df)})")
        
        # Filtros
        fc1, fc2 = st.columns(2)
        ftipo = fc1.multiselect("Filtrar por Tipo", df['tipo'].unique() if not df.empty else [])
        fstatus = fc2.multiselect("Filtrar por Status", df['status_venda'].unique() if not df.empty else [])
        
        df_show = df.copy()
        if ftipo: df_show = df_show[df_show['tipo'].isin(ftipo)]
        if fstatus: df_show = df_show[df_show['status_venda'].isin(fstatus)]
        
        st.dataframe(df_show, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("### ✏️ Editar / Gerenciar")
        
        sel_cli = st.selectbox("Selecione o cliente:", ["Selecione"] + df['nome'].tolist())
        
        if sel_cli != "Selecione":
            row = df[df['nome'] == sel_cli].iloc[0]
            id_sel = row['id']
            
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            ec1, ec2 = st.columns(2)
            enome = ec1.text_input("Nome", value=row['nome'])
            estat = ec2.selectbox("Status", ["Pendente", "Fechado Comigo", "Fechado com Outro", "Sem Interesse"], index=0)
            enota = st.text_area("Notas", value=row['notas'])
            
            c_up, c_del = st.columns([4, 1])
            if c_up.button("Atualizar Dados", type="primary"):
                db.update_cliente_completo(id_sel, {"nome": enome, "status_venda": estat, "notas": enota})
                st.success("Salvo!"); time.sleep(1); st.rerun()
            
            if c_del.button("🗑️"):
                db.delete_cliente(id_sel); st.success("Deletado!"); time.sleep(1); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)