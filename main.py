import streamlit as st
import database as db
import app_crm
import admin_panel
import email_utils
import time

# --- Configuração Global ---
st.set_page_config(
    page_title="Gestão Correspondente", 
    layout="wide", 
    page_icon="🟣", 
    initial_sidebar_state="expanded"
)
db.init_db()

# --- Inicialização de Estado ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'role' not in st.session_state: st.session_state.role = ''
if 'username' not in st.session_state: st.session_state.username = ''
if 'recup_etapa' not in st.session_state: st.session_state.recup_etapa = 0
if 'login_tab' not in st.session_state: st.session_state.login_tab = 'login'

# ==========================================
# CSS DINÂMICO (Separa Login de Dashboard)
# ==========================================

# 1. CSS GERAL (Fontes)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Esconder elementos nativos */
    #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 2. LÓGICA DE ESTILO
if not st.session_state.logged_in:
    # --- ESTILO TELA DE LOGIN (Fundo Roxo + Card Branco) ---
    st.markdown("""
        <style>
        /* Fundo Roxo Gradiente */
        .stApp {
            background: linear-gradient(135deg, #8A56E8 0%, #7A4FE3 100%);
        }
        
        /* O Cartão de Login (Container com borda) */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #ffffff;
            border-radius: 24px;
            padding: 2.5rem !important;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            border: 1px solid rgba(255,255,255,0.2);
            max-width: 450px;
            margin: auto;
        }
        
        /* Inputs Estilo Shadcn (Limpos) */
        .stTextInput input {
            height: 45px;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            padding: 0 12px;
            font-size: 14px;
            color: #1e293b;
            background-color: #f8fafc;
            transition: all 0.2s;
        }
        .stTextInput input:focus {
            border-color: #8b5cf6;
            background-color: #ffffff;
            box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2);
        }
        
        /* Botão Primário (Gradiente Violeta) */
        .stButton > button[kind="primary"] {
            width: 100%;
            background: linear-gradient(to right, #8b5cf6, #7c3aed);
            color: white;
            border: none;
            height: 48px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 15px;
            box-shadow: 0 4px 6px -1px rgba(124, 58, 237, 0.3);
            margin-top: 10px;
        }
        .stButton > button[kind="primary"]:hover {
            opacity: 0.9;
            transform: translateY(-1px);
            box-shadow: 0 10px 15px -3px rgba(124, 58, 237, 0.4);
        }
        
        /* Botão Secundário */
        .stButton > button[kind="secondary"] {
            background: white !important;
            color: #64748b !important;
            border: 1px solid #e2e8f0 !important;
            height: 40px;
        }

        /* Abas (Tabs) */
        .stTabs [data-baseweb="tab-list"] {
            gap: 20px;
            border-bottom: 1px solid #e2e8f0;
            margin-bottom: 20px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            color: #64748b;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            color: #7c3aed !important;
            border-bottom: 2px solid #7c3aed;
        }

        /* Centralização Vertical */
        div[data-testid="column"] { align-self: center; }
        </style>
    """, unsafe_allow_html=True)
else:
    # --- ESTILO SISTEMA (Fundo Limpo - SEM ROXO) ---
    st.markdown("""
        <style>
        /* Fundo Slate-50 (Cinza muito claro) */
        .stApp {
            background-color: #f8fafc !important;
            background-image: none !important;
        }
        
        /* Sidebar Branca Limpa */
        section[data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e2e8f0;
            box-shadow: 2px 0 10px rgba(0,0,0,0.01);
        }
        
        /* Inputs do Sistema */
        .stTextInput input {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
        }
        
        /* Botões do Menu Lateral */
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label {
            background-color: transparent;
            color: #64748b;
            border-radius: 8px;
            margin-bottom: 4px;
            padding: 10px 14px;
        }
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:hover {
            background-color: #f1f5f9;
            color: #7c3aed;
        }
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label[data-checked="true"] {
            background-color: #f5f3ff;
            color: #7c3aed;
            font-weight: 600;
            border: 1px solid #ddd6fe;
        }
        </style>
    """, unsafe_allow_html=True)


# ==========================================
# TELA DE LOGIN
# ==========================================
if not st.session_state.logged_in:
    
    st.write("")
    st.write("")
    
    # Layout centralizado
    col_esq, col_centro, col_dir = st.columns([1, 1.2, 1])
    
    with col_centro:
        # Usa container com borda para criar o "Quadrado" físico
        # O CSS acima estiliza esse bloco para ser branco com sombra
        with st.container(border=True):
            
            # Ícone Flutuante
            st.markdown("""
            <div style="display: flex; justify-content: center; margin-bottom: 1.5rem; margin-top: 0.5rem;">
                <div style="width: 64px; height: 64px; background: linear-gradient(135deg, #8b5cf6, #7c3aed); 
                            border-radius: 16px; display: flex; align-items: center; justify-content: center; 
                            box-shadow: 0 10px 15px -3px rgba(124, 58, 237, 0.3);">
                    <span style="font-size: 32px;">📄</span>
                </div>
            </div>
            <div style="text-align: center; margin-bottom: 2rem;">
                <h1 style="font-size: 24px; font-weight: 700; color: #1e293b; margin-bottom: 0.5rem; letter-spacing: -0.025em;">Gestão Correspondente</h1>
                <p style="color: #64748b; font-size: 14px; margin: 0;">Sistema CRM para Correspondentes Bancários</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Abas (Igual ao script novo que você gostou)
            tab_login, tab_register = st.tabs(["Entrar", "Criar Conta"])
            
            # --- LOGIN ---
            with tab_login:
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                
                st.markdown('<label style="font-size: 13px; font-weight: 500; color: #475569; margin-bottom: 6px; display: block;">Utilizador</label>', unsafe_allow_html=True)
                u = st.text_input("utilizador_input", placeholder="Seu nome de utilizador", key="log_u", label_visibility="collapsed")
                
                st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
                
                st.markdown('<label style="font-size: 13px; font-weight: 500; color: #475569; margin-bottom: 6px; display: block;">Senha</label>', unsafe_allow_html=True)
                p = st.text_input("senha_input", type="password", placeholder="••••••••••", key="log_p", label_visibility="collapsed")
                
                st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
                
                if st.button("Entrar no Sistema", use_container_width=True, type="primary"):
                    if u and p:
                        r = db.verificar_login(u, p)
                        if r['status'] == 'success':
                            if r['approved']:
                                st.session_state.logged_in = True
                                st.session_state.role = r['role']
                                st.session_state.username = u
                                st.rerun()
                            else: st.warning("🔒 Seu acesso ainda está pendente.")
                        else: st.error(r['msg'])
                    else: st.error("Preencha todos os campos")
            
            # --- REGISTRO ---
            with tab_register:
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                
                sub_tab_novo, sub_tab_recuperar = st.tabs(["Cadastro", "Recuperar Senha"])
                
                with sub_tab_novo:
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    c_reg1, c_reg2 = st.columns(2)
                    nu = c_reg1.text_input("Novo Usuário", placeholder="Login", key="reg_u")
                    ne = c_reg2.text_input("E-mail", placeholder="seu@email.com", key="reg_e")
                    np = c_reg1.text_input("Senha", type="password", key="reg_p")
                    npc = c_reg2.text_input("Confirmar", type="password", key="reg_pc")
                    
                    st.write("")
                    if st.button("Criar Conta", use_container_width=True, type="primary"):
                        if np != npc: st.error("Senhas não conferem.")
                        elif not all([nu, ne, np, npc]): st.error("Preencha todos os campos")
                        else:
                            res = db.registrar_usuario(nu, np, ne)
                            if res['status']:
                                st.success(f"Criado! ID: {res['id_gerado']}")
                                email_utils.email_boas_vindas(nu, ne)
                            else: st.error(res['msg'])
                
                with sub_tab_recuperar:
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    if st.session_state.recup_etapa == 0:
                        st.info("Digite seus dados para receber o código.")
                        ru = st.text_input("Seu Usuário", key="ru")
                        re = st.text_input("Seu E-mail", key="re")
                        if st.button("Enviar Código", use_container_width=True):
                            if ru and re:
                                res = db.iniciar_recuperacao_senha(ru, re)
                                if res['status']:
                                    email_utils.email_recuperacao(re, res['codigo'])
                                    st.session_state.recup_etapa = 1
                                    st.session_state.rec_user_temp = ru
                                    st.success("Enviado! Verifique o e-mail.")
                                else: st.error(res['msg'])
                    elif st.session_state.recup_etapa == 1:
                        st.success("Código enviado.")
                        rc = st.text_input("Código", placeholder="123456")
                        rn = st.text_input("Nova Senha", type="password")
                        c_b1, c_b2 = st.columns(2)
                        if c_b1.button("Voltar", use_container_width=True):
                            st.session_state.recup_etapa = 0; st.rerun()
                        if c_b2.button("Alterar", use_container_width=True, type="primary"):
                            if db.finalizar_recuperacao_senha(st.session_state.rec_user_temp, rc, rn):
                                st.success("Senha alterada!"); time.sleep(2)
                                st.session_state.recup_etapa = 0; st.rerun()
                            else: st.error("Erro.")

            # Footer
            st.markdown("""
            <div style="text-align: center; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #f1f5f9;">
                <p style="color: #94a3b8; font-size: 11px; margin: 0;">EDWCRED © 2026 • Sistema de Gestão</p>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# SISTEMA (LOGADO)
# ==========================================
else:
    with st.sidebar:
        # Card de Perfil Minimalista
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px; padding: 12px; margin-bottom: 24px; border: 1px solid #e2e8f0; border-radius: 12px; background: #ffffff;">
            <div style="width: 38px; height: 38px; background: #f5f3ff; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #7c3aed; font-weight: 700;">
                {st.session_state.username[0].upper()}
            </div>
            <div style="overflow: hidden;">
                <div style="font-weight: 600; color: #0f172a; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{st.session_state.username}</div>
                <div style="color: #64748b; font-size: 11px; font-weight: 500; text-transform: uppercase;">{st.session_state.role}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<p style='color: #94a3b8; font-size: 11px; font-weight: 600; padding-left: 8px; margin-bottom: 8px; letter-spacing: 0.05em;'>MENU PRINCIPAL</p>", unsafe_allow_html=True)
        
        opcoes_menu = ["📊 Dashboard", "👥 Clientes", "➕ Novo Cadastro"]
        if st.session_state.role == 'admin':
            opcoes_menu.append("🔒 Painel Admin")
            
        escolha = st.radio("Navegação", opcoes_menu, label_visibility="collapsed")
            
        st.markdown("---")
        if st.button("Sair", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # Roteamento
    if escolha == "🔒 Painel Admin":
        admin_panel.render_admin()
    else:
        mapa = {
            "📊 Dashboard": "Dashboard",
            "👥 Clientes": "Clientes",
            "➕ Novo Cadastro": "Novo Cadastro"
        }
        app_crm.render_page(mapa[escolha])
