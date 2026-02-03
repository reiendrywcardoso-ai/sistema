import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import time
import database as db 

# --- Helpers ---
LISTA_BANCOS = ["001 - Banco do Brasil", "033 - Santander", "104 - Caixa", "237 - Bradesco", "341 - Itaú", "260 - Nubank", "077 - Inter", "Outro"]
TIPOS_CHAVE_PIX = ["CPF", "Celular", "E-mail", "CNPJ", "Chave Aleatória"]
TIPOS_CONTA = ["Corrente", "Poupança", "Pagamento", "Salário"]

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
    # Cores baseadas no Tailwind (Violet, Blue, Green, Amber)
    bg_icon = "#f1f5f9"
    text_icon = "#475569"
    
    if cor_icone == "roxo":
        bg_icon = "#f3e8ff"; text_icon = "#7e22ce"
    elif cor_icone == "verde":
        bg_icon = "#dcfce7"; text_icon = "#15803d"
    elif cor_icone == "azul":
        bg_icon = "#dbeafe"; text_icon = "#1d4ed8"
    elif cor_icone == "laranja":
        bg_icon = "#ffedd5"; text_icon = "#c2410c"

    st.markdown(f"""
    <div class="dashboard-card" style="display: flex; align-items: start; justify-content: space-between; height: 100%;">
        <div>
            <p style="color: #64748b; font-size: 13px; font-weight: 600; margin: 0; text-transform: uppercase; letter-spacing: 0.5px;">{titulo}</p>
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
        st.sidebar.markdown("### 👁️ Filtro Admin")
        lista_users = ["Todos"] + db.get_lista_nomes_usuarios()
        filtro_usuario = st.sidebar.selectbox("Carteira:", lista_users)
    
    df = db.get_clientes(filtro_usuario)
    
    # Menu Superior
    menu = st.radio("", ["Dashboard", "Clientes", "Novo Cadastro"], horizontal=True, label_visibility="collapsed")
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # ==========================
    # DASHBOARD
    # ==========================
    if menu == "Dashboard":
        st.markdown(f"## Olá, <span style='color: #7c3aed'>{st.session_state.username}</span>! 👋", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748b; margin-top: -10px;'>Visão geral da sua carteira.</p>", unsafe_allow_html=True)
        
        # Métricas
        total = len(df)
        pendentes = len(df[df['status_venda'] == 'Pendente'])
        fechados = len(df[df['status_venda'].str.contains('Fechado', na=False)])
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: card_stats_moderno("Total Clientes", total, "Carteira ativa", "azul", "👥")
        with c2: card_stats_moderno("Pendentes", pendentes, "Ação necessária", "laranja", "⏳")
        with c3: card_stats_moderno("Fechados", fechados, "Contratos", "verde", "✅")
        
        # Lógica de Tarefas Automáticas (FGTS/CLT/Aniversário)
        hoje = datetime.now().date()
        tarefas = []
        
        # FGTS (10, 20, 26)
        if hoje.day in [10, 20, 26]:
            qtd_fgts = len(df[(df['tipo']=='FGTS') & (df['sub_categoria'].isin(['Sem Saldo', 'Antecipação Feita']))])
            if qtd_fgts > 0: tarefas.append(f"💰 {qtd_fgts} FGTS para consultar hoje")
        
        # Aniversariantes
        def chk_niver(d):
            try: x=pd.to_datetime(d); return x.day==hoje.day and x.month==hoje.month
            except: return False
        qtd_niver = len(df[df['data_nascimento'].apply(chk_niver)])
        if qtd_niver > 0: tarefas.append(f"🎂 {qtd_niver} Aniversariantes")

        with c4: 
            msg_tarefa = f"{len(tarefas)} Alertas" if tarefas else "Tudo em dia"
            card_stats_moderno("Tarefas Hoje", len(tarefas), msg_tarefa, "roxo", "📅")

        st.write("")
        st.write("")

        # Lista de Recentes
        st.markdown("### Clientes Recentes")
        st.markdown('<div class="dashboard-card" style="padding: 0; overflow: hidden;">', unsafe_allow_html=True)
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
                bg_st = "#f1f5f9"; cl_st = "#475569"
                if "Pendente" in r['status_venda']: bg_st = "#fff7ed"; cl_st = "#c2410c"
                if "Fechado" in r['status_venda']: bg_st = "#f0fdf4"; cl_st = "#15803d"

                st.markdown(f"""
                <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; padding: 16px 24px; border-bottom: 1px solid #f1f5f9; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div style="width: 36px; height: 36px; border-radius: 50%; background: #f1f5f9; display: flex; align-items: center; justify-content: center; font-weight: 600; color: #64748b;">
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
                        <span style="background: {bg_st}; color: {cl_st}; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 600;">{r['status_venda']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # ==========================
    # NOVO CADASTRO (COMPLETO)
    # ==========================
    elif menu == "Novo Cadastro":
        st.markdown("### Novo Cliente")
        with st.container():
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            
            # Dados Pessoais
            c1, c2 = st.columns(2)
            with c1:
                nn = st.text_input("Nome Completo", key="cad_nome")
                nc = st.text_input("CPF", key="cad_cpf")
                nt = st.selectbox("Tipo", ["INSS", "CLT", "FGTS"], key="cad_tipo")
                nas = st.date_input("Nascimento", min_value=date(1920, 1, 1), max_value=date(2030, 12, 31))
            with c2:
                ntel = st.text_input("Telefone", key="cad_tel")
                nsub = st.selectbox("Situação", ["Margem Livre", "Sem Margem", "Tem Saldo", "Sem Saldo", "Antecipação Feita"], key="cad_sub")
                
                # BUSCA DE CEP RESTAURADA
                col_cep, col_btn = st.columns([0.7, 0.3])
                ncep = col_cep.text_input("CEP", key="cad_cep")
                if col_btn.button("🔍 Buscar"):
                    d = buscar_endereco_cep(ncep)
                    if d:
                        st.session_state.cad_rua = d.get('logradouro','')
                        st.session_state.cad_bairro = d.get('bairro','')
                        st.session_state.cad_cid = d.get('localidade','')
                        st.session_state.cad_uf = d.get('uf','')
                        st.toast("Endereço encontrado!")
                    else: st.error("CEP não encontrado")

            # CAMPOS DE ENDEREÇO RESTAURADOS
            e1, e2 = st.columns(2)
            if 'cad_rua' not in st.session_state: st.session_state.cad_rua = ""
            if 'cad_num' not in st.session_state: st.session_state.cad_num = ""
            nrua = e1.text_input("Endereço", value=st.session_state.cad_rua, key="c_rua_in")
            nnum = e2.text_input("Número", key="c_num_in")
            
            e3, e4, e5 = st.columns(3)
            if 'cad_bairro' not in st.session_state: st.session_state.cad_bairro = ""
            if 'cad_cid' not in st.session_state: st.session_state.cad_cid = ""
            if 'cad_uf' not in st.session_state: st.session_state.cad_uf = ""
            nbai = e3.text_input("Bairro", value=st.session_state.cad_bairro, key="c_bai_in")
            ncid = e4.text_input("Cidade", value=st.session_state.cad_cid, key="c_cid_in")
            nuf = e5.text_input("UF", value=st.session_state.cad_uf, key="c_uf_in")
            
            nmae = st.text_input("Nome da Mãe", key="c_mae_in")

            st.markdown("---")
            st.caption("Financeiro (Completo)")
            
            f1, f2 = st.columns(2)
            with f1:
                tpix = st.selectbox("Tipo Pix", TIPOS_CHAVE_PIX)
                cpix = st.text_input("Chave Pix")
                if st.button("Adicionar Pix"):
                    st.session_state.temp_lists['cad_pix'].append(f"{tpix}: {cpix}")
                for p in st.session_state.temp_lists['cad_pix']: st.markdown(f"🔹 {p}")
            
            with f2:
                # BANCOS COMPLETOS RESTAURADOS
                bn = st.selectbox("Banco", LISTA_BANCOS)
                b_ag = st.text_input("Agência")
                b_cc = st.text_input("Conta")
                b_tipo = st.selectbox("Tipo Conta", TIPOS_CONTA)
                if st.button("Adicionar Conta"):
                    st.session_state.temp_lists['cad_bank'].append(f"{bn} | Ag: {b_ag} | Cc: {b_cc} ({b_tipo})")
                for b in st.session_state.temp_lists['cad_bank']: st.markdown(f"🏦 {b}")

            obs = st.text_area("Observações")
            
            st.write("")
            if st.button("SALVAR CADASTRO", type="primary", use_container_width=True):
                dados = {
                    "nome": nn, "telefone": ntel, "cpf": nc, "tipo": nt, "sub_categoria": nsub,
                    "status_venda": "Pendente", "data_nascimento": nas, "notas": obs,
                    "cep": ncep, "endereco": nrua, "numero": nnum, "bairro": nbai, "cidade": ncid, "estado": nuf, "nome_mae": nmae,
                    "pix_chave": " | ".join(st.session_state.temp_lists['cad_pix']),
                    "dados_bancarios": " || ".join(st.session_state.temp_lists['cad_bank']),
                    "usuario_responsavel": st.session_state.username
                }
                db.add_cliente(dados)
                st.success("Cliente cadastrado com sucesso!")
                st.session_state.temp_lists['cad_pix'] = []
                st.session_state.temp_lists['cad_bank'] = []
                # Limpa campos de endereco
                for k in ['cad_rua', 'cad_bairro', 'cad_cid', 'cad_uf']: st.session_state[k] = ""
                time.sleep(1); st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

    # ==========================
    # LISTA E EDIÇÃO
    # ==========================
    elif menu == "Clientes":
        st.markdown(f"### Carteira de Clientes")
        
        # Filtros
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
            
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            
            # Campos Básicos
            ec1, ec2 = st.columns(2)
            enome = ec1.text_input("Nome", value=row['nome'])
            ecpf = ec2.text_input("CPF", value=str(row['cpf']))
            
            ec3, ec4 = st.columns(2)
            etipo = ec3.selectbox("Tipo", ["INSS", "CLT", "FGTS"], index=["INSS", "CLT", "FGTS"].index(row['tipo']) if row['tipo'] in ["INSS", "CLT", "FGTS"] else 0)
            estat = ec4.selectbox("Status", ["Pendente", "Fechado Comigo", "Fechado com Outro", "Sem Interesse"], index=0)
            
            # Endereço na Edição
            st.markdown("#### Endereço")
            ec_cep, ec_btn = st.columns([0.7, 0.3])
            ecep = ec_cep.text_input("CEP", value=str(row['cep']))
            if ec_btn.button("🔍 Buscar CEP"):
                d = buscar_endereco_cep(ecep)
                if d: st.info(f"Endereço: {d.get('logradouro')}, {d.get('bairro')}")

            ee1, ee2 = st.columns(2)
            eend = ee1.text_input("Endereço", value=str(row['endereco']))
            enum = ee2.text_input("Número", value=str(row['numero']))
            
            ee3, ee4, ee5 = st.columns(3)
            ebai = ee3.text_input("Bairro", value=str(row['bairro']))
            ecid = ee4.text_input("Cidade", value=str(row['cidade']))
            eest = ee5.text_input("UF", value=str(row['estado']))
            
            emae = st.text_input("Mãe", value=str(row['nome_mae']))

            # Financeiro Edição (Texto livre para facilitar ou adicionar novos)
            st.markdown("#### Financeiro (Adicionar Novos)")
            ef1, ef2 = st.columns(2)
            with ef1:
                etpix = st.selectbox("Novo Pix Tipo", TIPOS_CHAVE_PIX, key="epix_t")
                ecpix = st.text_input("Chave", key="epix_c")
                if st.button("Add Pix", key="btn_add_pix_e"):
                    st.session_state.edit_pix_list.append(f"{etpix}: {ecpix}")
                
                # Lista Atual
                pix_atual = str(row['pix_chave']).split(' | ')
                st.caption("Pix Atuais (Edite abaixo se quiser remover tudo e salvar novos)")
                st.text_area("Pix Salvos", value=row['pix_chave'], key="final_pix_text")

            with ef2:
                ebn = st.selectbox("Novo Banco", LISTA_BANCOS, key="ebnk_n")
                ebag = st.text_input("Ag", key="ebnk_a")
                ebcc = st.text_input("Cc", key="ebnk_c")
                if st.button("Add Banco", key="btn_add_bnk_e"):
                    st.session_state.edit_bank_list.append(f"{ebn} Ag:{ebag} Cc:{ebcc}")
                
                st.caption("Bancos Atuais")
                st.text_area("Bancos Salvos", value=row['dados_bancarios'], key="final_bank_text")

            enota = st.text_area("Notas", value=row['notas'])
            
            c_up, c_del = st.columns([4, 1])
            if c_up.button("💾 Atualizar Dados", type="primary"):
                # Mescla o texto editado com os novos adicionados
                novos_pix = " | ".join(st.session_state.edit_pix_list)
                final_pix = f"{st.session_state.final_pix_text} | {novos_pix}" if novos_pix else st.session_state.final_pix_text
                
                novos_banks = " || ".join(st.session_state.edit_bank_list)
                final_bank = f"{st.session_state.final_bank_text} || {novos_banks}" if novos_banks else st.session_state.final_bank_text

                db.update_cliente_completo(id_sel, {
                    "nome": enome, "cpf": ecpf, "tipo": etipo, "status_venda": estat, 
                    "cep": ecep, "endereco": eend, "numero": enum, "bairro": ebai, "cidade": ecid, "estado": eest, "nome_mae": emae,
                    "pix_chave": final_pix, "dados_bancarios": final_bank, "notas": enota
                })
                st.session_state.edit_pix_list = []
                st.session_state.edit_bank_list = []
                st.success("Salvo!"); time.sleep(1); st.rerun()
            
            if c_del.button("🗑️"):
                db.delete_cliente(id_sel); st.success("Deletado!"); time.sleep(1); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)