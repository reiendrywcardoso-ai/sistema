import streamlit as st
import database as db
import app_crm
import admin_panel
import email_utils
import time

# --- Configuração Global ---
st.set_page_config(page_title="Gestão Correspondente", layout="wide", page_icon="🏦")
db.init_db()

# --- CSS MODERNO (Estilo da Imagem) ---
st.markdown("""
    <style>
    /* Fundo geral da página com gradiente moderno */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    /* Centralizar o container de login */
    div[data-testid="stVerticalBlock"] > div {
        display: flex;
        justify_content: center;
    }

    /* O Cartão de Login (Caixa Branca) */
    .login-container {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        width: 100%;
        max-width: 500px;
        margin: auto;
        text-align: center;
    }

    /* Títulos */
    h1 {
        color: #333 !important;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        font-size: 28px !important;
        text-align: center;
        margin-bottom: 5px !important;
    }
    
    h3 {
        color: #666 !important;
        font-size: 16px !important;
        text-align: center;
        margin-top: 0 !important;
        margin-bottom: 30px !important;
        font-weight: 400;
    }

    /* Botões Principais (Entrar/Registrar) */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px;
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(118, 75, 162, 0.4);
        color: white;
    }

    /* Inputs (Caixas de texto) */
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 1px solid #ddd;
        padding: 10px;
        background-color: #f9f9f9;
    }

    /* Abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        justify-content: center;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        border-radius: 20px;
        background-color: #f0f2f6;
        padding: 0 20px;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #764ba2 !important;
        color: white !important;
    }
    
    /* Esconder menu padrão do Streamlit na tela de login */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    </style>
""", unsafe_allow_html=True)

# --- Controle de Sessão ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'role' not in st.session_state: st.session_state.role = ''
if 'username' not in st.session_state: st.session_state.username = ''
if 'recup_etapa' not in st.session_state: st.session_state.recup_etapa = 0

# --- TELA DE LOGIN ---
def login_screen():
    # Usamos colunas vazias para centralizar o cartão no meio da tela
    col_vazia_esq, col_centro, col_vazia_dir = st.columns([1, 2, 1])
    
    with col_centro:
        # Início do Cartão Visual
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        st.title("🔐 Login")
        st.markdown("### Gestão de Correspondente")
        
        tab_login, tab_register = st.tabs(["Acessar Conta", "Criar Nova Conta"])
        
        # --- ABA ENTRAR ---
        with tab_login:
            st.write("") # Espaço
            u = st.text_input("Usuário", placeholder="Seu nome de usuário")
            p = st.text_input("Senha", type="password", placeholder="Sua senha")
            
            st.write("")
            if st.button("ENTRAR AGORA"):
                r = db.verificar_login(u, p)
                if r['status'] == 'success':
                    if r['approved']:
                        st.session_state.logged_in = True
                        st.session_state.role = r['role']
                        st.session_state.username = u
                        st.rerun()
                    else: st.warning("🔒 Seu cadastro aguarda aprovação.")
                else: st.error(r['msg'])
            
            st.markdown("---")
            with st.expander("Esqueci minha senha"):
                if st.session_state.recup_etapa == 0:
                    rec_user = st.text_input("Seu Usuário", key="rec_u")
                    rec_email = st.text_input("Seu E-mail", key="rec_e")
                    if st.button("Enviar Código"):
                        res = db.iniciar_recuperacao_senha(rec_user, rec_email)
                        if res['status']:
                            email_utils.email_recuperacao(rec_email, res['codigo'])
                            st.session_state.recup_etapa = 1
                            st.session_state.rec_user_temp = rec_user
                            st.success("Verifique seu e-mail!")
                            time.sleep(1)
                            st.rerun()
                        else: st.error(res['msg'])
                
                elif st.session_state.recup_etapa == 1:
                    st.info(f"Código enviado para: {st.session_state.rec_user_temp}")
                    rec_codigo = st.text_input("Código")
                    rec_nova_senha = st.text_input("Nova Senha", type="password", key="rec_np")
                    if st.button("Confirmar Mudança"):
                        if db.finalizar_recuperacao_senha(st.session_state.rec_user_temp, rec_codigo, rec_nova_senha):
                            st.success("Senha alterada! Faça login.")
                            st.session_state.recup_etapa = 0
                            time.sleep(2)
                            st.rerun()
                        else: st.error("Código inválido.")
                    if st.button("Cancelar"):
                        st.session_state.recup_etapa = 0
                        st.rerun()

        # --- ABA REGISTRAR ---
        with tab_register:
            st.write("")
            nu = st.text_input("Criar Usuário", placeholder="Escolha um login", key="reg_u")
            ne = st.text_input("Seu E-mail", placeholder="exemplo@email.com", key="reg_e")
            np = st.text_input("Criar Senha", type="password", key="reg_p")
            npc = st.text_input("Confirmar Senha", type="password", key="reg_pc")
            
            st.write("")
            if st.button("SOLICITAR ACESSO"):
                if not nu or not ne or not np:
                    st.warning("Preencha todos os campos.")
                elif np != npc:
                    st.error("As senhas não conferem.")
                else:
                    res = db.registrar_usuario(nu, np, ne)
                    if res['status']:
                        st.success(f"Sucesso! ID: #{res['id_gerado']}")
                        st.info("Aguarde o e-mail de aprovação.")
                        email_utils.email_boas_vindas(nu, ne)
                    else: st.error(res['msg'])

        st.markdown('</div>', unsafe_allow_html=True) # Fim do container

# --- ROTEAMENTO ---
if not st.session_state.logged_in:
    login_screen()
else:
    # --- RESETAR CSS QUANDO LOGADO (Voltar ao normal) ---
    # Injetamos um CSS mais leve para a área interna
    st.markdown("""
        <style>
        .stApp {background: #ffffff;} 
        /* Sidebar customizada */
        section[data-testid="stSidebar"] {
            background-color: #f8f9fa;
            border-right: 1px solid #eee;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.write(f"👤 Olá, **{st.session_state.username}**")
        st.caption(f"Perfil: {st.session_state.role}")
        
        pg = "CRM"
        if st.session_state.role == 'admin':
            pg = st.radio("Navegação", ["CRM", "Admin Panel"])
            
        st.markdown("---")
        if st.button("Sair / Logout"):
            st.session_state.logged_in = False
            st.rerun()
            
    if pg == "CRM": 
        app_crm.render_crm()
    elif pg == "Admin Panel": 
        admin_panel.render_admin()