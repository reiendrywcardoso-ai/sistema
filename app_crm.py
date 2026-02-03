import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import time
import database as db 

# --- Constantes ---
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

def verificar_regras_do_dia(df):
    if df.empty: return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    hoje = datetime.now().date()
    
    # 1. Pendentes
    mask_pend = ((df['status_venda'] == 'Pendente') & (((df['tipo'] == 'INSS') & (df['sub_categoria'] == 'Margem Livre')) | ((df['tipo'] == 'CLT') & (df['sub_categoria'] == 'Com Margem'))))
    df_p = df[mask_pend].copy()
    
    # 2. FGTS GERAL (Dia 10 ou 20-28)
    mask_fgts = pd.Series([False]*len(df))
    if hoje.day == 10 or (20 <= hoje.day <= 28):
        mask_fgts = ((df['tipo'] == 'FGTS') & (df['sub_categoria'].isin(['Sem Saldo', 'Antecipação Feita'])) & (df['status_venda'] != 'Fechado Comigo'))
    df_fgts_geral = df[mask_fgts].copy()

    # 3. CLT Quinzenal
    mask_clt = pd.Series([False]*len(df))
    if hoje.weekday() == 1 and (hoje.isocalendar()[1] % 2 == 0): 
        mask_clt = ((df['tipo'] == 'CLT') & (df['sub_categoria'] == 'Não Elegível') & (df['status_venda'] != 'Fechado com Outro'))
    df_c = df[mask_clt].copy()

    # 4. Aniversários
    def chk(d_str):
        try: d = pd.to_datetime(d_str); return d.day == hoje.day and d.month == hoje.month
        except: return False
    
    df['match'] = df['data_nascimento'].apply(chk)
    df_n = df[(df['match']) & (df['sub_categoria'] != 'Aguardando Aniversário')].copy()
    df_s = df[(df['match']) & (df['tipo'] == 'FGTS') & (df['sub_categoria'] == 'Aguardando Aniversário')].copy()

    return df_p, df_fgts_geral, df_c, df_n, df_s

# --- AQUI ESTÁ A FUNÇÃO QUE FALTAVA ---
def render_crm():
    # Inicializa variáveis
    variaveis_edicao = [
        'ed_nome', 'ed_cpf', 'ed_tel', 'ed_tipo', 'ed_sub', 'ed_stat', 
        'ed_cep', 'ed_end', 'ed_num', 'ed_bai', 'ed_cid', 
        'ed_uf', 'ed_mae', 'ed_pix_str', 'ed_bank_str', 'ed_nota',
        'ed_new_pix_key', 'ed_new_bank_cc' 
    ]
    for var in variaveis_edicao:
        if var not in st.session_state: st.session_state[var] = "" 

    if 'ed_nasc' not in st.session_state: st.session_state.ed_nasc = None
    if not st.session_state.ed_tipo: st.session_state.ed_tipo = "INSS"
    
    # Listas temporárias
    if 'cad_pix_list' not in st.session_state: st.session_state.cad_pix_list = []
    if 'cad_bank_list' not in st.session_state: st.session_state.cad_bank_list = []
    if 'edit_pix_list' not in st.session_state: st.session_state.edit_pix_list = []
    if 'edit_bank_list' not in st.session_state: st.session_state.edit_bank_list = []

    st.title(f"Bem vindo, {st.session_state.username}!")
    
    # Filtro Admin/User
    filtro_usuario = st.session_state.username 
    if st.session_state.role == 'admin':
        st.markdown("### 👁️ Visão de Administrador")
        lista_users = ["Todos"] + db.get_lista_nomes_usuarios()
        filtro_usuario = st.selectbox("Ver carteira de clientes de:", lista_users)
    
    df = db.get_clientes(filtro_usuario)
    st.write(f"**Data de Hoje:** {datetime.now().strftime('%d/%m/%Y')}")

    # --- CADASTRO ---
    st.markdown('<div class="btn-incluir">', unsafe_allow_html=True)
    mostrar_cadastro = st.expander("➕ Incluir Novo Cliente", expanded=False)
    st.markdown('</div>', unsafe_allow_html=True)

    with mostrar_cadastro:
        st.markdown("### Ficha de Cadastro")
        c1, c2, c3 = st.columns(3)
        with c1:
            n_nome = st.text_input("Nome", key="cad_nome")
            n_cpf = st.text_input("CPF", key="cad_cpf")
            n_tel = st.text_input("Telefone", key="cad_tel")
        with c2:
            n_tipo = st.selectbox("Tipo", ["INSS", "CLT", "FGTS"], key="cad_tipo")
            ops = []
            if n_tipo == "INSS": ops = ["Margem Livre", "Portabilidade", "Sem Margem"]
            elif n_tipo == "CLT": ops = ["Com Margem", "Sem Margem", "Não Elegível"]
            else: ops = ["Tem Saldo", "Sem Saldo", "Antecipação Feita", "Aguardando Aniversário"]
            n_sub = st.selectbox("Situação", ops, key="cad_sub")
            n_nasc = st.date_input("Data/Lembrete", min_value=date(1920, 1, 1), max_value=date(2030, 12, 31), format="DD/MM/YYYY", key="cad_nasc")
        with c3:
            st.write("**Endereço**")
            cx, cy = st.columns([0.7, 0.3])
            c_cep = cx.text_input("CEP", max_chars=9, key="cad_cep_in")
            def busca_cad():
                d = buscar_endereco_cep(st.session_state.cad_cep_in)
                if d:
                    st.session_state.cad_rua = d.get('logradouro','')
                    st.session_state.cad_bairro = d.get('bairro','')
                    st.session_state.cad_cid = d.get('localidade','')
                    st.session_state.cad_uf = d.get('uf','')
            cy.button("🔍", on_click=busca_cad)

        e1, e2 = st.columns(2)
        v_rua = e1.text_input("Logradouro", key="cad_rua")
        v_num = e2.text_input("Número", key="cad_num")
        e3, e4, e5 = st.columns(3)
        v_bai = e3.text_input("Bairro", key="cad_bairro")
        v_cid = e4.text_input("Cidade", key="cad_cid")
        v_uf = e5.text_input("UF", key="cad_uf")
        v_mae = st.text_input("Mãe", key="cad_mae")

        st.markdown("---")
        fp1, fp2 = st.columns(2)
        with fp1:
            st.caption("Pix")
            px1, px2, px3 = st.columns([0.4, 0.4, 0.2])
            tp = px1.selectbox("Tipo", TIPOS_CHAVE_PIX, key="tmp_pix_t")
            cp = px2.text_input("Chave", key="tmp_pix_c")
            def add_pix_cad():
                if st.session_state.tmp_pix_c:
                    st.session_state.cad_pix_list.append(f"{st.session_state.tmp_pix_t}: {st.session_state.tmp_pix_c}")
                    st.session_state.tmp_pix_c = ""
            px3.button("Add", on_click=add_pix_cad, key="btn_apc")
            for p in st.session_state.cad_pix_list: st.markdown(f"<div class='item-lista'>{p}</div>", unsafe_allow_html=True)
            if st.button("Limpar Pix", key="clr_pix_c"): st.session_state.cad_pix_list = []

        with fp2:
            st.caption("Bancos")
            bk1, bk2 = st.columns([0.6, 0.4])
            bn = bk1.selectbox("Banco", LISTA_BANCOS, key="tmp_bnk_n")
            ba = bk2.text_input("Ag", key="tmp_bnk_a")
            bk3, bk4, bk5 = st.columns([0.5, 0.3, 0.2])
            bc = bk3.text_input("Cc", key="tmp_bnk_c")
            bo = bk4.text_input("Op", key="tmp_bnk_o")
            def add_bnk_cad():
                if bn and bc:
                    st.session_state.cad_bank_list.append(f"{bn} | Ag:{ba} Cc:{bc} Op:{bo}")
                    st.session_state.tmp_bnk_c = ""
            bk5.button("Add", on_click=add_bnk_cad, key="btn_abc")
            for b in st.session_state.cad_bank_list: st.markdown(f"<div class='item-lista'>{b}</div>", unsafe_allow_html=True)
            if st.button("Limpar Bancos", key="clr_bnk_c"): st.session_state.cad_bank_list = []

        v_nota = st.text_area("Obs", key="cad_notas")
        if st.button("💾 SALVAR", type="primary"):
            status_i = "Pendente"
            if n_sub == "Sem Margem" and n_tipo == "CLT": status_i = "Sem Interesse"
            dados = {
                "nome": n_nome, "telefone": n_tel, "cpf": n_cpf, "tipo": n_tipo, "sub_categoria": n_sub,
                "status_venda": status_i, "data_nascimento": n_nasc, "notas": v_nota,
                "cep": c_cep, "endereco": v_rua, "numero": v_num, "bairro": v_bai, "cidade": v_cid,
                "estado": v_uf, "nome_mae": v_mae,
                "pix_chave": " | ".join(st.session_state.cad_pix_list),
                "dados_bancarios": " || ".join(st.session_state.cad_bank_list),
                "usuario_responsavel": st.session_state.username
            }
            db.add_cliente(dados)
            st.success("Salvo!")
            st.session_state.cad_pix_list = []
            st.session_state.cad_bank_list = []
            time.sleep(1)
            st.rerun()

    # --- ABAS ---
    tab1, tab2 = st.tabs(["🔔 Lembretes", "📋 Gestão / Editar"])
    
    with tab1:
        if df.empty: st.info("Sem dados.")
        else:
            pend, fgts_geral, clt, niver, saque = verificar_regras_do_dia(df)
            if not saque.empty:
                st.markdown(f'<div class="saque-aniv"><h3>⏳ LIBEROU ({len(saque)})</h3></div>', unsafe_allow_html=True)
                for i, r in saque.iterrows():
                    with st.expander(f"{r['nome']}"):
                         if st.button("Consultado ✅", key=f"sa_{r['id']}"):
                             db.update_status(r['id'], "Fechado Comigo"); st.rerun()
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Pendentes")
                for i, r in pend.iterrows():
                    with st.expander(f"{r['nome']}"):
                        st.write(f"📞 {r['telefone']}")
                        if st.button("Fechou ✅", key=f"pfm_{r['id']}"):
                            db.update_status(r['id'], "Fechado Comigo"); st.rerun()
                st.subheader("Aniversários")
                if not niver.empty: st.dataframe(niver[['nome','telefone']], hide_index=True)
            with c2:
                st.subheader("Automático")
                if not fgts_geral.empty:
                    st.warning(f"FGTS ({len(fgts_geral)})")
                    st.dataframe(fgts_geral[['nome','telefone']], hide_index=True)
                if not clt.empty:
                    st.info(f"CLT ({len(clt)})")
                    st.dataframe(clt[['nome','telefone']], hide_index=True)

    with tab2:
        st.header(f"Base: {filtro_usuario}")
        filtro = st.multiselect("Filtrar", df['tipo'].unique() if not df.empty else [])
        df_s = df[df['tipo'].isin(filtro)] if filtro else df
        st.dataframe(df_s, hide_index=True)

        if not df.empty:
            st.markdown("---")
            st.subheader("✏️ Editar Cliente")
            lista_clientes = df.apply(lambda x: f"{x['id']} - {x['nome']}", axis=1).tolist()
            cliente_escolhido = st.selectbox("Selecione:", lista_clientes)
            
            if 'last_cli_sel' not in st.session_state or st.session_state.last_cli_sel != cliente_escolhido:
                st.session_state.last_cli_sel = cliente_escolhido
                if cliente_escolhido:
                    id_sel = int(cliente_escolhido.split(' - ')[0])
                    row = df[df['id'] == id_sel].iloc[0]
                    st.session_state.ed_nome = row['nome']; st.session_state.ed_cpf = row['cpf']
                    st.session_state.ed_tel = row['telefone']; st.session_state.ed_tipo = row['tipo']
                    st.session_state.ed_sub = row['sub_categoria']; st.session_state.ed_stat = row['status_venda']
                    st.session_state.ed_nasc = pd.to_datetime(row['data_nascimento']).date() if row['data_nascimento'] else None
                    st.session_state.ed_cep = row['cep']; st.session_state.ed_end = row['endereco']
                    st.session_state.ed_num = row['numero']; st.session_state.ed_bai = row['bairro']
                    st.session_state.ed_cid = row['cidade']; st.session_state.ed_uf = row['estado']
                    st.session_state.ed_mae = row['nome_mae']; st.session_state.ed_nota = row['notas']
                    st.session_state.edit_pix_list = [p.strip() for p in str(row['pix_chave']).split('|') if p.strip()]
                    st.session_state.edit_bank_list = [b.strip() for b in str(row['dados_bancarios']).split('||') if b.strip()]

            if cliente_escolhido:
                id_sel = int(cliente_escolhido.split(' - ')[0])
                ec1, ec2 = st.columns(2)
                with ec1: st.text_input("Nome", key="ed_nome"); st.text_input("CPF", key="ed_cpf")
                with ec2: st.text_input("Telefone", key="ed_tel"); st.date_input("Data", key="ed_nasc")
                
                tipos = ["INSS", "CLT", "FGTS"]
                try: idx_t = tipos.index(st.session_state.ed_tipo)
                except: idx_t = 0
                nt = st.selectbox("Tipo", tipos, index=idx_t, key="ed_tipo")
                
                ops_e = []
                if nt == "INSS": ops_e = ["Margem Livre", "Portabilidade", "Sem Margem"]
                elif nt == "CLT": ops_e = ["Com Margem", "Sem Margem", "Não Elegível"]
                else: ops_e = ["Tem Saldo", "Sem Saldo", "Antecipação Feita", "Aguardando Aniversário"]
                
                try: idx_s = ops_e.index(st.session_state.ed_sub)
                except: idx_s = 0
                st.selectbox("Situação", ops_e, index=idx_s, key="ed_sub")
                
                stats = ["Pendente", "Fechado Comigo", "Fechado com Outro", "Sem Interesse", "Consultado"]
                try: idx_st = stats.index(st.session_state.ed_stat)
                except: idx_st = 0
                st.selectbox("Status", stats, index=idx_st, key="ed_stat")

                st.write("**Endereço**")
                c_cep, c_btn = st.columns([0.8, 0.2])
                st.text_input("CEP", key="ed_cep")
                if c_btn.button("🔍", key="btn_be"):
                    d = buscar_endereco_cep(st.session_state.ed_cep)
                    if d:
                        st.session_state.ed_end = d.get('logradouro','')
                        st.session_state.ed_bai = d.get('bairro','')
                        st.session_state.ed_cid = d.get('localidade','')
                        st.session_state.ed_uf = d.get('uf','')

                e1, e2 = st.columns(2)
                st.text_input("Endereço", key="ed_end"); st.text_input("Número", key="ed_num")
                e3, e4, e5 = st.columns(3)
                st.text_input("Bairro", key="ed_bai"); st.text_input("Cidade", key="ed_cid"); st.text_input("UF", key="ed_uf")
                st.text_input("Mãe", key="ed_mae")

                st.markdown("---")
                fpe1, fpe2 = st.columns(2)
                with fpe1:
                    st.caption("Pix (Edição)")
                    pe1, pe2, pe3 = st.columns([0.4, 0.4, 0.2])
                    tp = pe1.selectbox("Tipo", TIPOS_CHAVE_PIX, key="ed_pt")
                    cp = pe2.text_input("Chave", key="ed_pc")
                    def add_pix_ed():
                        if st.session_state.ed_pc:
                            st.session_state.edit_pix_list.append(f"{st.session_state.ed_pt}: {st.session_state.ed_pc}")
                            st.session_state.ed_pc = ""
                    pe3.button("Add", on_click=add_pix_ed, key="btn_ape")
                    for idx, p in enumerate(st.session_state.edit_pix_list):
                        st.markdown(f"<div class='item-lista'>{p}</div>", unsafe_allow_html=True)
                        if st.button("🗑️", key=f"rm_pix_{idx}"):
                            st.session_state.edit_pix_list.pop(idx); st.rerun()

                with fpe2:
                    st.caption("Bancos (Edição)")
                    be1, be2 = st.columns([0.6, 0.4])
                    bn = be1.selectbox("Banco", LISTA_BANCOS, key="ed_bn")
                    ba = be2.text_input("Ag", key="ed_ba")
                    be3, be4, be5 = st.columns([0.5, 0.3, 0.2])
                    bc = be3.text_input("Cc", key="ed_bc")
                    bo = be4.text_input("Op", key="ed_bo")
                    def add_bnk_ed():
                        if bn and bc:
                            st.session_state.edit_bank_list.append(f"{bn} | Ag:{ba} Cc:{bc} Op:{bo}")
                            st.session_state.ed_bc = ""
                    be5.button("Add", on_click=add_bnk_ed, key="btn_abe")
                    for idx, b in enumerate(st.session_state.edit_bank_list):
                        st.markdown(f"<div class='item-lista'>{b}</div>", unsafe_allow_html=True)
                        if st.button("🗑️", key=f"rm_bnk_{idx}"):
                            st.session_state.edit_bank_list.pop(idx); st.rerun()

                st.text_area("Notas", key="ed_nota")

                if st.button("💾 Salvar Alterações", type="primary"):
                    dados_up = {
                        'nome': st.session_state.ed_nome, 'telefone': st.session_state.ed_tel, 'cpf': st.session_state.ed_cpf,
                        'tipo': st.session_state.ed_tipo, 'sub_categoria': st.session_state.ed_sub, 'status_venda': st.session_state.ed_stat,
                        'data_nascimento': st.session_state.ed_nasc, 'notas': st.session_state.ed_nota, 'cep': st.session_state.ed_cep,
                        'endereco': st.session_state.ed_end, 'numero': st.session_state.ed_num, 'bairro': st.session_state.ed_bai,
                        'cidade': st.session_state.ed_cid, 'estado': st.session_state.ed_uf, 'nome_mae': st.session_state.ed_mae,
                        'pix_chave': " | ".join(st.session_state.edit_pix_list), 'dados_bancarios': " || ".join(st.session_state.edit_bank_list)
                    }
                    db.update_cliente_completo(id_sel, dados_up)
                    st.success("Atualizado!"); time.sleep(1); st.rerun()

                st.markdown("---")
                with st.expander("🗑️ Excluir Cliente"):
                    if st.checkbox(f"Confirmar exclusão de **{st.session_state.ed_nome}**"):
                        if st.button("EXCLUIR"): db.delete_cliente(id_sel); st.success("Feito."); time.sleep(1); st.rerun()