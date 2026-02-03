import streamlit as st
import database as db
import app_crm
import admin_panel
import email_utils
import time

# --- Configuração Global ---
st.set_page_config(page_title="Gestão Correspondente", layout="wide", page_icon="🟣")
db.init_db()

# --- CSS GLOBAL (TRADUÇÃO DO DESIGN REACT/TAILWIND) ---
st.markdown("""
    <style>
    /* Importando a fonte Inter (usada no design original) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1e293b; /* Slate-800 */
    }

    /* Fundo da Aplicação (Cinza/Branco suave) */
    .stApp {
        background-color: #f8fafc; /* Slate-50 */
    }

    /* Esconder menus padrões */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Sidebar Estilo Dashboard */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0; /* Slate-200 */
    }

    /* ESTILO DOS CARDS (Igual ao Shadcn UI) */
    .dashboard-card {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-radius: 0.75rem; /* rounded-xl */
        padding: 1.5rem;
        box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1); /* shadow-sm */
    }

    /* Botões Principais (Gradiente Violeta) */
    .stButton>button {
        background: linear-gradient(to right, #8b5cf6, #7c3aed); /* violet-500 to violet-600 */
        color: white;
        border: none;
        border-radius: 0.5rem; /* rounded-lg */
        padding: 0.5rem 1rem;
        font-weight: 500;
        letter-spacing: 0.025em;
        transition: all 0.2s;
        box-shadow: 0 4px 6px -1px rgba(124, 58, 237, 0.3);
    }
    
    .stButton>button:hover {
        opacity: 0.9;
        transform: translateY(-1px);
        box-shadow: 0 6px 8px -1px rgba(124, 58, 237, 0.4);
        color: white;
    }

    /* Inputs (Campos de Texto) Estilo Shadcn */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div, .stDateInput input, .stTextArea textarea {
        border-radius: 0.5rem; /* rounded-lg */
        border: 1px solid #e2e8f0; /* slate-200 */
        background-color: #ffffff;
        color: #0f172a; /* slate-900 */
        padding: 0.5rem 0.75rem;
        height: auto;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #8b5cf6; /* violet-500 */
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2); /* ring-violet */
    }

    /* Títulos */
    h1, h2, h3 {
        color: #0f172a; /* slate-900 */
        font-weight: 700;
        letter-spacing: -0.025em;
    }
    
    /* Login Container Específico */
    .login-glass {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: 1.5rem; /* rounded-3xl */
        padding: 3rem;
        box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- Sessão ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'role' not in st.session_state: st.session_state.role = ''
if 'username' not in st.session_state: st.session_state.username = ''
if 'recup_etapa' not in st.session_state: st.session_state.recup_etapa = 0

# ==========================================
# TELA DE LOGIN (ESTILO GLASS/VIOLETA)
# ==========================================
if not st.session_state.logged_in:
    # CSS Específico só para o fundo do login
    st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #e9d5ff, #f3e8ff, #ffffff);
        /* Um fundo suave roxo/branco como no design moderno */
    }
    </style>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.write("")
        st.write("")
        
        # Container Glassmorphism
        st.markdown('<div class="login-glass">', unsafe_allow_html=True)
        
        # Logo/Ícone
        st.markdown("""
        <div style="display: flex; justify-content: center; margin-bottom: 24px;">
            <div style="background: linear-gradient(135deg, #7c3aed, #6d28d9); width: 64px; height: 64px; border-radius: 16px; display: flex; align-items: center; justify-content: center; color: white; font-size: 32px; box-shadow: 0 10px 15px -3px rgba(124, 58, 237, 0.3);">
                🏦
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<h2 style='text-align: center; margin-bottom: 8px;'>Bem-vindo</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b; font-size: 14px; margin-bottom: 32px;'>Gestão de Correspondente Bancário</p>", unsafe_allow_html=True)
        
        tab_login, tab_register = st.tabs(["Acessar", "Criar Conta"])
        
        with tab_login:
            u = st.text_input("Usuário", placeholder="Seu login", key="log_u")
            p = st.text_input("Senha", type="password", placeholder="••••••••", key="log_p")
            
            st.write("")
            if st.button("ENTRAR", use_container_width=True):
                r = db.verificar_login(u, p)
                if r['status'] == 'success':
                    if r['approved']:
                        st.session_state.logged_in = True
                        st.session_state.role = r['role']
                        st.session_state.username = u
                        st.rerun()
                    else: st.warning("Aguardando aprovação.")
                else: st.error(r['msg'])
            
            with st.expander("Esqueceu a senha?"):
                if st.session_state.recup_etapa == 0:
                    ru = st.text_input("Usuário", key="ru")
                    re = st.text_input("E-mail", key="re")
                    if st.button("Enviar Código"):
                        res = db.iniciar_recuperacao_senha(ru, re)
                        if res['status']:
                            email_utils.email_recuperacao(re, res['codigo'])
                            st.session_state.recup_etapa = 1
                            st.session_state.rec_user_temp = ru
                            st.success("Enviado!"); time.sleep(1); st.rerun()
                        else: st.error(res['msg'])
                elif st.session_state.recup_etapa == 1:
                    rc = st.text_input("Código")
                    rn = st.text_input("Nova Senha", type="password")
                    if st.button("Confirmar"):
                        if db.finalizar_recuperacao_senha(st.session_state.rec_user_temp, rc, rn):
                            st.success("Senha alterada!"); st.session_state.recup_etapa = 0; time.sleep(1); st.rerun()
                        else: st.error("Erro.")

        with tab_register:
            nu = st.text_input("Novo Usuário", key="reg_u")
            ne = st.text_input("E-mail", key="reg_e")
            np = st.text_input("Senha", type="password", key="reg_p")
            npc = st.text_input("Confirmar", type="password", key="reg_pc")
            
            if st.button("SOLICITAR ACESSO", use_container_width=True):
                if np != npc: st.error("Senhas não batem.")
                else:
                    res = db.registrar_usuario(nu, np, ne)
                    if res['status']:
                        st.success(f"ID: {res['id_gerado']}")
                        email_utils.email_boas_vindas(nu, ne)
                    else: st.error(res['msg'])

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 12px; margin-top: 24px;'>EDWCRED © 2026</p>", unsafe_allow_html=True)

# --- ÁREA INTERNA ---
else:
    with st.sidebar:
        # Perfil com Design Moderno
        st.markdown(f"""
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; display: flex; align-items: center; gap: 12px; margin-bottom: 24px;">
            <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #8b5cf6, #7c3aed); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                {st.session_state.username[0].upper()}
            </div>
            <div>
                <div style="font-weight: 600; color: #0f172a; font-size: 14px;">{st.session_state.username}</div>
                <div style="color: #64748b; font-size: 11px; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px;">{st.session_state.role}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        pg = "CRM"
        if st.session_state.role == 'admin':
            pg = st.radio("Menu", ["CRM", "Painel Admin"])
            
        st.markdown("---")
        if st.button("Sair", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    if pg == "CRM": 
        app_crm.render_crm()
    elif pg == "Painel Admin": 
        admin_panel.render_admin()