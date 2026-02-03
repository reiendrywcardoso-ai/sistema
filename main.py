import streamlit as st
import database as db
import app_crm
import admin_panel
import email_utils
import time

st.set_page_config(page_title="CRM Pro", layout="wide", page_icon="🔐")
db.init_db()

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; }
    .btn-incluir button { background-color: #00b894; color: white; }
    .saque-aniv { background-color: #ffeaa7; padding: 10px; border-radius: 5px; border-left: 5px solid #fdcb6e; }
    .item-lista { background-color: #f1f2f6; padding: 5px; margin-bottom: 5px; border-left: 3px solid #0984e3; }
    .btn-excluir button { background-color: #ff4757 !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'role' not in st.session_state: st.session_state.role = ''
if 'username' not in st.session_state: st.session_state.username = ''
if 'recup_etapa' not in st.session_state: st.session_state.recup_etapa = 0 # 0=Nada, 1=Codigo Enviado

if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.title("🔐 Login CRM")
        t1, t2 = st.tabs(["Entrar", "Criar Conta"])
        
        with t1:
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.button("ENTRAR", type="primary"):
                r = db.verificar_login(u, p)
                if r['status'] == 'success':
                    if r['approved']:
                        st.session_state.logged_in = True
                        st.session_state.role = r['role']
                        st.session_state.username = u
                        st.rerun()
                    else: st.warning("Aguardando aprovação.")
                else: st.error(r['msg'])
            
            # --- AREA DE RECUPERAÇÃO DE SENHA ---
            st.markdown("---")
            with st.expander("🔑 Esqueci minha senha"):
                if st.session_state.recup_etapa == 0:
                    st.write("Digite seus dados para receber o código.")
                    rec_user = st.text_input("Seu Usuário", key="rec_u")
                    rec_email = st.text_input("Seu E-mail", key="rec_e")
                    
                    if st.button("Enviar Código de Recuperação"):
                        res = db.iniciar_recuperacao_senha(rec_user, rec_email)
                        if res['status']:
                            email_utils.email_recuperacao(rec_email, res['codigo'])
                            st.session_state.recup_etapa = 1
                            st.session_state.rec_user_temp = rec_user # Guarda usuario para proxima etapa
                            st.success("Código enviado para o e-mail! Verifique (inclusive spam).")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(res['msg'])
                
                elif st.session_state.recup_etapa == 1:
                    st.success(f"Código enviado para o usuário: {st.session_state.rec_user_temp}")
                    rec_codigo = st.text_input("Digite o Código recebido no E-mail")
                    rec_nova_senha = st.text_input("Nova Senha", type="password", key="rec_np")
                    
                    if st.button("Alterar Senha"):
                        if db.finalizar_recuperacao_senha(st.session_state.rec_user_temp, rec_codigo, rec_nova_senha):
                            st.success("Senha alterada com sucesso! Faça login.")
                            st.session_state.recup_etapa = 0
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("Código incorreto.")
                    
                    if st.button("Voltar / Cancelar"):
                        st.session_state.recup_etapa = 0
                        st.rerun()

        with t2:
            st.info("Preencha para solicitar acesso.")
            nu = st.text_input("Novo Usuário", key="reg_u")
            ne = st.text_input("E-mail", key="reg_e")
            np = st.text_input("Senha", type="password", key="reg_p")
            npc = st.text_input("Confirmar Senha", type="password", key="reg_pc")
            
            if st.button("REGISTRAR"):
                if not nu or not ne or not np:
                    st.warning("Preencha todos os campos.")
                elif np != npc:
                    st.error("As senhas não são iguais.")
                else:
                    resultado = db.registrar_usuario(nu, np, ne)
                    if resultado['status']:
                        st.success(f"Solicitado com sucesso! ID: #{resultado['id_gerado']}")
                        st.info("Aguarde o e-mail de aprovação.")
                        email_utils.email_boas_vindas(nu, ne)
                    else:
                        st.error(resultado['msg'])

else:
    with st.sidebar:
        st.write(f"👤 **{st.session_state.username}**")
        pg = "CRM"
        if st.session_state.role == 'admin': pg = st.radio("Menu", ["CRM", "Admin Panel"])
        st.markdown("---")
        if st.button("Sair"):
            st.session_state.logged_in = False
            st.rerun()
            
    if pg == "CRM": app_crm.render_crm()
    elif pg == "Admin Panel": admin_panel.render_admin()