import streamlit as st
import database as db
import app_crm
import admin_panel
import email_utils
import time

# --- Configuração Global ---
st.set_page_config(page_title="Gestão Correspondente", layout="wide", page_icon="🟣")
db.init_db()

# --- CSS GLOBAL PREMIUM (ROXO/VIOLETA) ---
st.markdown("""
    <style>
    /* Fonte Moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Fundo Geral da Aplicação */
    .stApp {
        background-color: #f8f9fe; /* Fundo cinza/azulado bem claro */
    }

    /* Esconder menus padrões */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Sidebar (Menu Lateral) */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #f1f3f9;
        box-shadow: 2px 0 10px rgba(0,0,0,0.02);
    }

    /* Botões Principais (Gradiente Roxo) */
    .stButton>button {
        background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%); /* Roxo Degradê */
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(109, 40, 217, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(109, 40, 217, 0.4);
        color: white;
    }

    /* Botões Secundários (Brancos/Outline) */
    button[kind="secondary"] {
        background: white;
        border: 1px solid #e5e7eb;
        color: #374151;
    }

    /* Inputs (Campos de Texto) */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div, .stDateInput input, .stTextArea textarea {
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        background-color: #ffffff;
        color: #1e293b;
        padding: 10px;
        transition: border 0.2s;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #8b5cf6;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2);
    }

    /* Cards Personalizados (HTML) */
    .custom-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05);
        border: 1px solid #f1f5f9;
        margin-bottom: 20px;
    }

    /* Métricas no Dashboard */
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #1e293b;
    }
    .metric-label {
        font-size: 14px;
        color: #64748b;
        font-weight: 500;
    }

    /* Estilo do Login */
    .login-container {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        padding: 40px;
        border-radius: 24px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# --- Sessão ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'role' not in st.session_state: st.session_state.role = ''
if 'username' not in st.session_state: st.session_state.username = ''
if 'recup_etapa' not in st.session_state: st.session_state.recup_etapa = 0

# ==========================================
# TELA DE LOGIN (ESTILO DO ARQUIVO .TXT)
# ==========================================
if not st.session_state.logged_in:
    # Sobrescreve fundo APENAS para o login
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #a78bfa 0%, #7c3aed 50%, #4c1d95 100%);
    }
    </style>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.write("")
        st.write("")
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Ícone
        st.markdown("""
        <div style="display: flex; justify-content: center; margin-bottom: 20px;">
            <div style="background: linear-gradient(135deg, #8b5cf6, #6d28d9); width: 60px; height: 60px; border-radius: 15px; display: flex; align-items: center; justify-content: center; box-shadow: 0 10px 25px -5px rgba(124, 58, 237, 0.5);">
                <span style="font-size: 30px;">🟣</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<h2 style='text-align: center; color: #1e293b; margin-bottom: 5px;'>Bem-vindo de volta</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b; font-size: 14px; margin-bottom: 30px;'>Acesse o painel de gestão</p>", unsafe_allow_html=True)
        
        tab_entrar, tab_criar = st.tabs(["Login", "Criar Conta"])
        
        with tab_entrar:
            u = st.text_input("Usuário", placeholder="Digite seu usuário", key="log_u")
            p = st.text_input("Senha", type="password", placeholder="••••••••", key="log_p")
            
            st.write("")
            if st.button("ENTRAR NA CONTA", use_container_width=True):
                r = db.verificar_login(u, p)
                if r['status'] == 'success':
                    if r['approved']:
                        st.session_state.logged_in = True
                        st.session_state.role = r['role']
                        st.session_state.username = u
                        st.rerun()
                    else: st.warning("🔒 Aguardando aprovação do admin.")
                else: st.error(r['msg'])
            
            with st.expander("Esqueceu a senha?"):
                if st.session_state.recup_etapa == 0:
                    ru = st.text_input("Seu Usuário", key="ru")
                    re = st.text_input("Seu E-mail", key="re")
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

        with tab_criar:
            nu = st.text_input("Novo Usuário", key="reg_u")
            ne = st.text_input("E-mail", key="reg_e")
            np = st.text_input("Senha", type="password", key="reg_p")
            npc = st.text_input("Confirmar", type="password", key="reg_pc")
            
            st.write("")
            if st.button("SOLICITAR ACESSO", use_container_width=True):
                if np != npc: st.error("Senhas não batem.")
                else:
                    res = db.registrar_usuario(nu, np, ne)
                    if res['status']:
                        st.success(f"ID: {res['id_gerado']}")
                        email_utils.email_boas_vindas(nu, ne)
                    else: st.error(res['msg'])

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: rgba(255,255,255,0.7); margin-top: 20px; font-size: 12px;'>EDWCRED © 2026</p>", unsafe_allow_html=True)

# --- ÁREA INTERNA ---
else:
    with st.sidebar:
        # Perfil com gradiente
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f8f7ff 0%, #eef2ff 100%); padding: 20px; border-radius: 16px; margin-bottom: 20px; border: 1px solid #e0e7ff;">
            <div style="font-weight: 700; color: #1e293b; font-size: 16px;">{st.session_state.username}</div>
            <div style="font-size: 12px; color: #6366f1; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">{st.session_state.role}</div>
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