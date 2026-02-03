import streamlit as st
import database as db
import app_crm
import admin_panel
import email_utils
import time

# --- Configuração Global ---
st.set_page_config(page_title="Gestão Correspondente", layout="wide", page_icon="🟣", initial_sidebar_state="expanded")
db.init_db()

# --- CSS DO TEST.PY ADAPTADO PARA WEB ---
st.markdown("""
    <style>
    /* Fonte Padrão */
    html, body, [class*="css"] {
        font-family: 'Arial', sans-serif;
    }

    /* 1. Fundo da Janela (Roxo Sólido do test.py) */
    .stApp {
        background-color: #8A56E8;
    }

    /* Esconder menus padrões */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 2. Sidebar (Menu Lateral) - Fundo Branco Limpo */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }

    /* 3. Cartão de Login (Lilás Claro do test.py) */
    .login-card {
        background-color: #F3EFFE;
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        text-align: center;
    }

    /* 4. Botões (Roxo Vibrante do test.py) */
    .stButton>button {
        background-color: #7A4FE3;
        color: white;
        border: none;
        border-radius: 12px;
        height: 45px;
        font-weight: bold;
        font-size: 16px;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #673FD0;
        color: white;
        transform: translateY(-2px);
    }

    /* 5. Inputs (Caixas de Texto) */
    .stTextInput input {
        border-radius: 8px;
        border: 2px solid #E0E0E0;
        padding: 10px 15px;
        background-color: white;
        color: #333;
    }
    .stTextInput input:focus {
        border-color: #7A4FE3;
    }

    /* --- ESTILO DO MENU LATERAL (Para não ficar branco invisível) --- */
    /* Remove a bolinha do radio button */
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label > div:first-child {
        display: none;
    }
    
    /* Botão do menu normal */
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label {
        background-color: transparent;
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 5px;
        border: 1px solid transparent;
        color: #666; /* Texto Cinza Escuro */
        font-weight: 500;
        cursor: pointer;
        width: 100%;
        display: flex;
    }

    /* Botão do menu SELECIONADO (Fica Lilás igual ao cartão) */
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #F3EFFE !important;
        color: #7A4FE3 !important;
        font-weight: bold;
        border: 1px solid #7A4FE3;
    }
    
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:hover {
        background-color: #f8fafc;
        color: #7A4FE3;
    }
    </style>
""", unsafe_allow_html=True)

# --- Sessão ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'role' not in st.session_state: st.session_state.role = ''
if 'username' not in st.session_state: st.session_state.username = ''
if 'recup_etapa' not in st.session_state: st.session_state.recup_etapa = 0

# ==========================================
# TELA DE LOGIN (DESIGN DO TEST.PY)
# ==========================================
if not st.session_state.logged_in:
    
    # Centralizar
    c1, c2, c3 = st.columns([1, 1.2, 1])
    
    with c2:
        st.write(""); st.write("")
        
        # Início do Cartão
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        # Ícone Redondo Roxo
        st.markdown("""
        <div style="display: flex; justify-content: center; margin-bottom: 20px;">
            <div style="background-color: #7A4FE3; width: 70px; height: 70px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 35px; box-shadow: 0 5px 15px rgba(122, 79, 227, 0.4);">
                👤
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<h2 style='color: #333; margin: 0;'>Bem-vindo</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #666; font-size: 14px; margin-bottom: 25px;'>Faça login para continuar</p>", unsafe_allow_html=True)
        
        tab_login, tab_register = st.tabs(["Login", "Registar"])
        
        # ABA LOGIN
        with tab_login:
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            u = st.text_input("Utilizador", placeholder="Seu nome", key="log_u")
            p = st.text_input("Senha", type="password", placeholder="••••••••", key="log_p")
            
            st.write("")
            # Botão com setinha igual ao test.py
            if st.button("Entrar   →", use_container_width=True):
                r = db.verificar_login(u, p)
                if r['status'] == 'success':
                    if r['approved']:
                        st.session_state.logged_in = True
                        st.session_state.role = r['role']
                        st.session_state.username = u
                        st.rerun()
                    else: st.warning("Aguarde aprovação.")
                else: st.error(r['msg'])
            
            with st.expander("Esqueceu a senha?"):
                if st.session_state.recup_etapa == 0:
                    ru = st.text_input("Usuário", key="ru")
                    re = st.text_input("E-mail", key="re")
                    if st.button("Enviar Código"):
                        res = db.iniciar_recuperacao_senha(ru, re)
                        if res['status']:
                            email_utils.email_recuperacao(re, res['codigo'])
                            st.session_state.recup_etapa = 1; st.session_state.rec_user_temp = ru
                            st.success("Enviado!"); time.sleep(1); st.rerun()
                        else: st.error(res['msg'])
                elif st.session_state.recup_etapa == 1:
                    rc = st.text_input("Código"); rn = st.text_input("Nova Senha", type="password")
                    if st.button("Confirmar"):
                        if db.finalizar_recuperacao_senha(st.session_state.rec_user_temp, rc, rn):
                            st.success("Senha alterada!"); st.session_state.recup_etapa = 0; time.sleep(1); st.rerun()
                        else: st.error("Erro.")

        # ABA REGISTRO
        with tab_register:
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            nu = st.text_input("Novo Usuário", key="reg_u")
            ne = st.text_input("E-mail", key="reg_e")
            np = st.text_input("Senha", type="password", key="reg_p")
            npc = st.text_input("Confirmar", type="password", key="reg_pc")
            
            st.write("")
            if st.button("Criar Conta   →", use_container_width=True):
                if np != npc: st.error("Senhas não batem.")
                else:
                    res = db.registrar_usuario(nu, np, ne)
                    if res['status']: st.success(f"ID: {res['id_gerado']}"); email_utils.email_boas_vindas(nu, ne)
                    else: st.error(res['msg'])

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: rgba(255,255,255,0.7); margin-top: 20px; font-size: 11px;'>EDWCRED © 2026</p>", unsafe_allow_html=True)

# ==========================================
# ÁREA INTERNA (SISTEMA)
# ==========================================
else:
    # Remove o fundo roxo forte aqui dentro para não cansar a vista
    st.markdown("""
        <style>
        .stApp { background-color: #f8fafc; }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        # Card de Perfil com as cores do tema
        st.markdown(f"""
        <div style="background-color: #F3EFFE; border: 1px solid #7A4FE3; border-radius: 12px; padding: 16px; display: flex; align-items: center; gap: 12px; margin-bottom: 24px;">
            <div style="width: 40px; height: 40px; background: #7A4FE3; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                {st.session_state.username[0].upper()}
            </div>
            <div style="overflow: hidden;">
                <div style="font-weight: 700; color: #333; font-size: 14px;">{st.session_state.username}</div>
                <div style="color: #7A4FE3; font-size: 11px; font-weight: 600; text-transform: uppercase;">{st.session_state.role}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<p style='color: #666; font-size: 12px; font-weight: 600; padding-left: 5px; margin-bottom: 10px;'>NAVEGAÇÃO</p>", unsafe_allow_html=True)
        
        # --- MENU LATERAL QUE VOCÊ QUERIA ---
        opcoes_menu = ["📊 Dashboard", "👥 Clientes", "➕ Novo Cadastro"]
        
        if st.session_state.role == 'admin':
            opcoes_menu.append("🔒 Painel Admin")
            
        escolha = st.radio("Menu", opcoes_menu, label_visibility="collapsed")
            
        st.markdown("---")
        if st.button("Sair", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # --- ROTEAMENTO ---
    if escolha == "🔒 Painel Admin":
        admin_panel.render_admin()
    else:
        # Mapeamento para o app_crm
        mapa = {
            "📊 Dashboard": "Dashboard",
            "👥 Clientes": "Clientes",
            "➕ Novo Cadastro": "Novo Cadastro"
        }
        app_crm.render_page(mapa[escolha])