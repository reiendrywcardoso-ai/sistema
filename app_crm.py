import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import time
import database as db 

# --- Helpers ---
LISTA_BANCOS = [
  "001 - Banco do Brasil",
  "003 - Banco da Amazônia",
  "004 - Banco do Nordeste",
  "021 - Banestes",
  "025 - Banco Alfa",
  "033 - Santander",
  "041 - Banrisul",
  "070 - BRB",
  "077 - Inter",
  "082 - Banrisul",
  "085 - Ailos",
  "097 - Cresol",
  "104 - Caixa",
  "121 - Agibank",
  "197 - Stone",
  "208 - BTG Pactual",
  "212 - Banco Original",
  "237 - Bradesco",
  "246 - ABC Brasil",
  "260 - Nubank",
  "290 - PagBank",
  "318 - BMG",
  "323 - Mercado Pago",
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
  "654 - Neon",
  "735 - Neon Pagamentos",
  "745 - Citibank",
  "748 - Sicredi",
  "756 - Sicoob",
  "Outro"
]
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

def card_stats_react(titulo, valor, subtitulo, cor_tema, icone):
    # Cores inspiradas no seu arquivo TXT
    bg_icon = "#f1f5f9"; text_icon = "#475569"
    if cor_tema == "violet": bg_icon = "#f3e8ff"; text_icon = "#7c3aed"
    elif cor_tema == "green": bg_icon = "#dcfce7"; text_icon = "#16a34a"
    elif cor_tema == "blue": bg_icon = "#dbeafe"; text_icon = "#2563eb"
    elif cor_tema == "amber": bg_icon = "#ffedd5"; text_icon = "#ea580c"

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

def render_page(pagina_atual):
    # Inicializa variáveis de endereço
    for k in ['cad_rua', 'cad_bairro', 'cad_cid', 'cad_uf', 'cad_num']:
        if k not in st.session_state: st.session_state[k] = ""

    vars_ed = ['ed_nome', 'ed_cpf', 'ed_tel', 'ed_tipo', 'ed_sub', 'ed_stat', 'ed_cep', 'ed_end', 'ed_num', 'ed_bai', 'ed_cid', 'ed_uf', 'ed_mae', 'ed_pix_str', 'ed_bank_str', 'ed_nota']
    for v in vars_ed:
        if v not in st.session_state: st.session_state[v] = ""
    if 'ed_nasc' not in st.session_state: st.session_state.ed_nasc = None
    if 'temp_lists' not in st.session_state: st.session_state.temp_lists = {'cad_pix':[], 'cad_bank':[], 'ed_pix':[], 'ed_bank':[]}

    filtro_usuario = st.session_state.username 
    if st.session_state.role == 'admin':
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Filtro Admin**")
        lista_users = ["Todos"] + db.get_lista_nomes_usuarios()
        filtro_usuario = st.sidebar.selectbox("Ver dados de:", lista_users)
    
    df = db.get_clientes(filtro_usuario)
    
    if pagina_atual == "Dashboard":
        st.markdown(f"## Olá, {st.session_state.username}")
        st.markdown("<p style='color: #64748b;'>Visão geral da sua carteira hoje.</p>", unsafe_allow_html=True)
    elif pagina_atual == "Clientes":
        st.markdown("## Carteira de Clientes")
    elif pagina_atual == "Novo Cadastro":
        st.markdown("## Novo Cadastro")

    st.write("") 

    # ==========================
    # DASHBOARD
    # ==========================
    if pagina_atual == "Dashboard":
        total = len(df)
        pendentes = len(df[df['status_venda'] == 'Pendente'])
        fechados = len(df[df['status_venda'].str.contains('Fechado', na=False)])
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: card_stats_react("Total Clientes", total, "Carteira ativa", "blue", "👥")
        with c2: card_stats_react("Pendentes", pendentes, "Ação necessária", "amber", "⏳")
        with c3: card_stats_react("Fechados", fechados, "Contratos finalizados", "green", "✅")
        
        hoje = datetime.now().date()
        tarefas = []
        if hoje.day in [10, 20, 26]:
            qtd_fgts = len(df[(df['tipo']=='FGTS') & (df['sub_categoria'].isin(['Sem Saldo', 'Antecipação Feita']))])
            if qtd_fgts > 0: tarefas.append(f"💰 {qtd_fgts} FGTS")
        
        def chk_niver(d):
            try: x=pd.to_datetime(d); return x.day==hoje.day and x.month==hoje.month
            except: return False
        qtd_niver = len(df[df['data_nascimento'].apply(chk_niver)])
        if qtd_niver > 0: tarefas.append(f"🎂 {qtd_niver} Aniversários")

        with c4: 
            msg = f"{len(tarefas)} Alertas" if tarefas else "Tudo em dia"
            card_stats_react("Tarefas Hoje", len(tarefas), msg, "violet", "📅")

        st.write("")
        col_left, col_right = st.columns([2, 1])

        with col_left:
            st.markdown("### Clientes Recentes")
            st.markdown('<div class="react-card" style="padding: 0; overflow: hidden;">', unsafe_allow_html=True)
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
                            <span style="background: {bg_st}; color: {cl_st}; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 600;">{r['status_venda']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("<div style='padding: 24px; text-align: center; color: #94a3b8;'>Nenhum dado.</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_right:
            st.markdown("### Lembretes")
            st.markdown('<div class="react-card">', unsafe_allow_html=True)
            if tarefas:
                for t in tarefas:
                    st.markdown(f"<div style='margin-bottom: 10px; font-weight: 500;'>• {t}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<p style='color: #94a3b8;'>Nenhum lembrete.</p>", unsafe_allow_html=True)
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
                nt = st.selectbox("Tipo", ["INSS", "CLT", "FGTS"], key="cad_tipo")
                nas = st.date_input("Nascimento", min_value=date(1920, 1, 1), max_value=date(2030, 12, 31))
            with c2:
                ntel = st.text_input("Telefone", key="cad_tel")
                nsub = st.selectbox("Situação", ["Margem Livre", "Sem Margem", "Tem Saldo", "Sem Saldo", "Antecipação Feita"], key="cad_sub")
                
                # BUSCA CEP
                col_cep, col_btn = st.columns([0.7, 0.3])
                ncep = col_cep.text_input("CEP", key="cad_cep")
                if col_btn.button("🔍"):
                    d = buscar_endereco_cep(ncep)
                    if d:
                        st.session_state.cad_rua = d.get('logradouro', '')
                        st.session_state.cad_bairro = d.get('bairro', '')
                        st.session_state.cad_cid = d.get('localidade', '')
                        st.session_state.cad_uf = d.get('uf', '')
                        st.toast("Endereço encontrado!")
                        st.rerun()
                    else: st.error("CEP inválido")

            st.markdown("---")
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

            obs = st.text_area("Observações")
            
            st.write("")
            if st.button("SALVAR CADASTRO", use_container_width=True):
                dados = {
                    "nome": nn, "telefone": ntel, "cpf": nc, "tipo": nt, "sub_categoria": nsub,
                    "status_venda": "Pendente", "data_nascimento": nas, "notas": obs,
                    "cep": ncep, "endereco": nrua, "numero": nnum, "bairro": nbai, "cidade": ncid, "estado": nuf, "nome_mae": nmae,
                    "pix_chave": " | ".join(st.session_state.temp_lists['cad_pix']),
                    "dados_bancarios": " || ".join(st.session_state.temp_lists['cad_bank']),
                    "usuario_responsavel": st.session_state.username
                }
                db.add_cliente(dados)
                st.success("Salvo!")
                st.session_state.temp_lists['cad_pix'] = []
                st.session_state.temp_lists['cad_bank'] = []
                for k in ['cad_rua', 'cad_bairro', 'cad_cid', 'cad_uf', 'cad_num']: st.session_state[k] = ""
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
            etipo = ec3.selectbox("Tipo", ["INSS", "CLT", "FGTS"], index=["INSS", "CLT", "FGTS"].index(row['tipo']) if row['tipo'] in ["INSS", "CLT", "FGTS"] else 0)
            estat = ec4.selectbox("Status", ["Pendente", "Fechado Comigo", "Fechado com Outro", "Sem Interesse"], index=0)
            
            st.markdown("#### Endereço")
            col_ecep, col_ebtn = st.columns([0.7, 0.3])
            ecep = col_ecep.text_input("CEP", value=str(row['cep']), key="e_cep_in")
            if col_ebtn.button("🔍 Buscar", key="btn_e_cep"):
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
            
            ee3, ee4, ee5 = st.columns(3)
            ebai = ee3.text_input("Bairro", value=val_bai)
            ecid = ee4.text_input("Cidade", value=val_cid)
            eest = ee5.text_input("UF", value=val_uf)
            emae = st.text_input("Mãe", value=str(row['nome_mae']))

            st.markdown("#### Financeiro")
            ef1, ef2 = st.columns(2)
            with ef1:
                # Pix
                etpix = st.selectbox("Pix Tipo", TIPOS_CHAVE_PIX, key="ept")
                ecpix = st.text_input("Chave", key="epc")
                if st.button("Add Pix", key="bap"):
                    st.session_state.edit_pix_list.append(f"{etpix}: {ecpix}")
                
                pix_db = str(row['pix_chave']).split(" | ")
                all_pix = pix_db + st.session_state.edit_pix_list
                st.write("**Pix Salvos:**")
                for p in all_pix: 
                    if p: st.caption(p)

            with ef2:
                # Banco (Completo na Edição também)
                ebn = st.selectbox("Banco", LISTA_BANCOS, key="ebn")
                ebag = st.text_input("Ag", key="eba")
                ebcc = st.text_input("Cc", key="ebc")
                ebtp = st.selectbox("Tipo", TIPOS_CONTA, key="ebtp")
                if st.button("Add Banco", key="bab"):
                    st.session_state.edit_bank_list.append(f"{ebn} | Ag:{ebag} Cc:{ebcc} ({ebtp})")
                
                bank_db = str(row['dados_bancarios']).split(" || ")
                all_bank = bank_db + st.session_state.edit_bank_list
                st.write("**Bancos Salvos:**")
                for b in all_bank:
                    if b: st.caption(b)

            enota = st.text_area("Notas", value=row['notas'])
            
            c_up, c_del = st.columns([4, 1])
            if c_up.button("ATUALIZAR DADOS", type="primary"):
                final_pix = " | ".join([p for p in all_pix if p])
                final_bank = " || ".join([b for b in all_bank if b])
                
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