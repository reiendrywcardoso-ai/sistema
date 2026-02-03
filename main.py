import streamlit as st
import database as db
import app_crm
import admin_panel
import email_utils
import time

# --- Configuração Global ---
st.set_page_config(page_title="Gestão Correspondente", layout="wide", page_icon="🏦")
db.init_db()

# --- CSS LEVE (Apenas para esconder menus chatos e centralizar) ---
st.markdown("""
    <style>
    /* Esconder menu do Streamlit para parecer um App nativo */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Estilo do container de login */
    .login-box {
        border: 1px solid #e6e6e6;
        padding: 30px;
        border-radius: 10px;
        background-color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- Controle de Sessão ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'role' not in st.session_state: st.session_state.role = ''
if 'username' not in st.session_state: st.session_state.username = ''
if 'recup_etapa' not in st.session_state: st.session_state.recup_etapa = 0

# --- TELA DE LOGIN ---
if not st.session_state.logged_in:
    # Colunas para centralizar (1 parte vazia, 1 parte conteúdo, 1 parte vazia)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    
    with c2:
        st.markdown("<h1 style='text-align: center;'>🏦 Gestão de Correspondente</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: grey;'>Faça login para acessar o sistema.</p>", unsafe_allow_html=True)
        st.divider()
        
        # Abas simples e limpas
        tab_login, tab_register = st.tabs(["🔐 Entrar", "📝 Criar Conta"])
        
        with tab_login:
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            
            # Botão grande usando use_container_width
            if st.button("ACESSAR SISTEMA", type="primary", use_container_width=True):
                r = db.verificar_login(u, p)
                if r['status'] == 'success':
                    if r['approved']:
                        st.session_state.logged_in = True
                        st.session_state.role = r['role']
                        st.session_state.username = u
                        st.rerun()
                    else:
                        st.warning("🔒 Seu cadastro ainda está pendente de aprovação.")
                else:
                    st.error(r['msg'])
            
            st.markdown("")
            with st.expander("Esqueci a minha senha"):
                if st.session_state.recup_etapa == 0:
                    st.caption("Informe seus dados para receber o código.")
                    rec_user = st.text_input("Seu Usuário", key="rec_u")
                    rec_email = st.text_input("Seu E-mail", key="rec_e")
                    
                    if st.button("Enviar Código de Recuperação"):
                        res = db.iniciar_recuperacao_senha(rec_user, rec_email)
                        if res['status']:
                            email_utils.email_recuperacao(rec_email, res['codigo'])
                            st.session_state.recup_etapa = 1
                            st.session_state.rec_user_temp = rec_user
                            st.success("Verifique seu e-mail (inclusive spam).")
                            time.sleep(1)
                            st.rerun()
                        else: st.error(res['msg'])
                
                elif st.session_state.recup_etapa == 1:
                    st.info(f"Código enviado para: **{st.session_state.rec_user_temp}**")
                    rec_codigo = st.text_input("Digite o Código")
                    rec_nova_senha = st.text_input("Nova Senha", type="password", key="rec_np")
                    
                    c_voltar, c_confirmar = st.columns(2)
                    if c_confirmar.button("Confirmar", type="primary"):
                        if db.finalizar_recuperacao_senha(st.session_state.rec_user_temp, rec_codigo, rec_nova_senha):
                            st.success("Senha alterada! Faça login.")
                            st.session_state.recup_etapa = 0
                            time.sleep(2)
                            st.rerun()
                        else: st.error("Código incorreto.")
                    
                    if c_voltar.button("Cancelar"):
                        st.session_state.recup_etapa = 0
                        st.rerun()

        with tab_register:
            st.caption("Preencha para solicitar acesso ao administrador.")
            nu = st.text_input("Escolha um Usuário", key="reg_u")
            ne = st.text_input("Seu E-mail", key="reg_e")
            np = st.text_input("Escolha uma Senha", type="password", key="reg_p")
            npc = st.text_input("Confirme a Senha", type="password", key="reg_pc")
            
            if st.button("SOLICITAR CADASTRO", use_container_width=True):
                if not nu or not ne or not np:
                    st.warning("Preencha todos os campos.")
                elif np != npc:
                    st.error("As senhas não conferem.")
                else:
                    res = db.registrar_usuario(nu, np, ne)
                    if res['status']:
                        st.success(f"Solicitado! ID: #{res['id_gerado']}")
                        st.info("Aguarde o e-mail de aprovação.")
                        email_utils.email_boas_vindas(nu, ne)
                    else: st.error(res['msg'])

# --- SISTEMA LOGADO ---
else:
    # Sidebar Limpa
    with st.sidebar:
        st.title("Menu")
        st.write(f"👤 **{st.session_state.username}**")
        
        pg = "CRM"
        if st.session_state.role == 'admin':
            pg = st.radio("Navegar", ["CRM", "Painel Admin"])
            
        st.markdown("---")
        if st.button("Sair", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
            
    # Carrega a página correta
    if pg == "CRM": 
        app_crm.render_crm()
    elif pg == "Painel Admin": 
        admin_panel.render_admin()