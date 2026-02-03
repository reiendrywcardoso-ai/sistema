import streamlit as st
import database as db
import app_crm
import admin_panel
import email_utils
import time

# --- Configuração Global ---
st.set_page_config(page_title="Gestão Correspondente", layout="wide", page_icon="🟣", initial_sidebar_state="expanded")
db.init_db()

# --- CSS SUPREMO (RECRIAÇÃO EXATA DO DESIGN REACT/SHADCN) ---
st.markdown("""
    <style>
    /* 1. Fonte Inter (A mesma do design system) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #0f172a;
    }

    /* 2. Fundo Geral */
    .stApp {
        background-color: #f8fafc;
        background-image: radial-gradient(at 0% 0%, rgba(139, 92, 246, 0.15) 0px, transparent 50%), 
                          radial-gradient(at 100% 100%, rgba(124, 58, 237, 0.15) 0px, transparent 50%);
        background-attachment: fixed;
    }

    /* 3. Esconder elementos nativos */
    #MainMenu, footer, header {visibility: hidden;}

    /* 4. Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
        box-shadow: 2px 0 10px rgba(0,0,0,0.01);
    }

    /* 5. Menu Lateral */
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label > div:first-child { display: none; }
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label {
        background-color: transparent;
        padding: 10px 14px;
        border-radius: 8px;
        margin-bottom: 4px;
        color: #64748b;
        font-weight: 500;
        border: 1px solid transparent;
        transition: all 0.2s;
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

    /* 6. Card de Login */
    .shadcn-card {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-radius: 1rem;
        padding: 2.5rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025);
        max-width: 100%;
    }

    /* 7. Inputs */
    .stTextInput input {
        height: 45px;
        border-radius: 0.5rem;
        border: 1px solid #e2e8f0;
        padding: 0 12px;
        font-size: 14px;
        color: #1e293b;
        background-color: white;
        transition: all 0.2s;
    }
    .stTextInput input:focus {
        border-color: #8b5cf6;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2);
    }

    /* 8. Botão Primário */
    .stButton > button[kind="primary"] {
        width: 100%;
        background: linear-gradient(to right, #8b5cf6, #7c3aed);
        color: white;
        border: none;
        height: 45px;
        border-radius: 0.5rem;
        font-weight: 500;
        font-size: 15px;
        box-shadow: 0 4px 6px -1px rgba(124, 58, 237, 0.3);
        transition: transform 0.1s;
    }
    .stButton > button[kind="primary"]:hover {
        opacity: 0.9;
        transform: translateY(-1px);
        box-shadow: 0 6px 10px -1px rgba(124, 58, 237, 0.4);
        color: white;
    }

    /* 9. Botão Secundário */
    .stButton > button[kind="secondary"] {
        background: white !important;
        color: #64748b !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1) !important;
        height: 45px;
    }
    .stButton > button[kind="secondary"]:hover {
        background: #f8fafc !important;
        border-color: #cbd5e1 !important;
        color: #334155 !important;
    }

    /* 10. Link para esqueci senha */
    .link-esqueci {
        background: transparent !important;
        border: none !important;
        color: #8b5cf6 !important;
        font-size: 12px !important;
        padding: 0 !important;
        height: auto !important;
        box-shadow: none !important;
        text-align: right;
        font-weight: 500;
    }
    .link-esqueci:hover {
        color: #7c3aed !important;
        text-decoration: underline;
    }

    /* Títulos */
    h1, h2, h3 { font-family: 'Inter', sans-serif; letter-spacing: -0.025em; }
    
    div[data-testid="stVerticalBlock"] { gap: 0rem; }
    </style>
""", unsafe_allow_html=True)

# --- Sessão ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'role' not in st.session_state: st.session_state.role = ''
if 'username' not in st.session_state: st.session_state.username = ''
if 'recup_etapa' not in st.session_state: st.session_state.recup_etapa = 0
if 'login_tab' not in st.session_state: st.session_state.login_tab = 'login'
if 'register_subtab' not in st.session_state: st.session_state.register_subtab = 'criar'

# ==========================================
# TELA DE LOGIN
# ==========================================
if not st.session_state.logged_in:
    
    col_esq, col_centro, col_dir = st.columns([1, 1.2, 1])
    
    with col_centro:
        st.write("") 
        st.write("") 
        
        st.markdown('<div class="shadcn-card">', unsafe_allow_html=True)
        
        # Caixa branca decorativa (da imagem)
        st.markdown("""
        <div style="text-align: center; margin-bottom: -30px;">
            <div style="width: 420px; height: 100px; background: white; border: 1px solid #e2e8f0; 
                        border-radius: 12px; margin: 0 auto; box-shadow: 0 2px 4px rgba(0,0,0,0.02);"></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Cabeçalho
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem; position: relative; z-index: 2;">
            <div style="width: 72px; height: 72px; background: linear-gradient(135deg, #8b5cf6, #7c3aed); 
                        border-radius: 16px; display: inline-flex; align-items: center; justify-content: center; 
                        margin: 0 auto 1.5rem auto; box-shadow: 0 4px 6px -1px rgba(124, 58, 237, 0.2);">
                <span style="font-size: 36px;">📱</span>
            </div>
            <h1 style="font-size: 28px; font-weight: 700; color: #0f172a; margin-bottom: 0.5rem;">Gestão Correspondente</h1>
            <p style="color: #64748b; font-size: 14px; margin: 0;">Sistema CRM para Correspondentes Bancários</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Botões Entrar / Registar
        col_entrar, col_registar = st.columns(2)
        
        with col_entrar:
            if st.session_state.login_tab == 'login':
                st.markdown("""
                <div style="text-align: center; padding: 12px; background: white; border-bottom: 2px solid #7c3aed; 
                            font-weight: 600; color: #0f172a; font-size: 15px;">
                    Entrar
                </div>
                """, unsafe_allow_html=True)
            else:
                if st.button("Entrar", key="btn_entrar", use_container_width=True, type="secondary"):
                    st.session_state.login_tab = 'login'
                    st.rerun()
        
        with col_registar:
            if st.session_state.login_tab == 'register':
                st.markdown("""
                <div style="text-align: center; padding: 12px; background: white; border-bottom: 2px solid #7c3aed; 
                            font-weight: 600; color: #0f172a; font-size: 15px;">
                    Registar
                </div>
                """, unsafe_allow_html=True)
            else:
                if st.button("Registar", key="btn_registar", use_container_width=True, type="secondary"):
                    st.session_state.login_tab = 'register'
                    st.session_state.register_subtab = 'criar'
                    st.rerun()
        
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
        
        # --- TELA DE LOGIN ---
        if st.session_state.login_tab == 'login':
            
            st.markdown('<label style="font-size: 14px; font-weight: 500; color: #334155; display: block; margin-bottom: 0.5rem;">Utilizador</label>', unsafe_allow_html=True)
            
            col_icon_user, col_input_user = st.columns([0.08, 0.92])
            with col_icon_user:
                st.markdown('<div style="padding-top: 12px; font-size: 18px; color: #64748b;">👤</div>', unsafe_allow_html=True)
            with col_input_user:
                u = st.text_input("utilizador_input", placeholder="Seu nome de utilizador", key="log_u", label_visibility="collapsed")
            
            st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
            
            st.markdown('<label style="font-size: 14px; font-weight: 500; color: #334155; display: block; margin-bottom: 0.5rem;">Senha</label>', unsafe_allow_html=True)
            
            col_icon_pass, col_input_pass = st.columns([0.08, 0.92])
            with col_icon_pass:
                st.markdown('<div style="padding-top: 12px; font-size: 18px; color: #64748b;">🔒</div>', unsafe_allow_html=True)
            with col_input_pass:
                p = st.text_input("senha_input", type="password", placeholder="••••••••", key="log_p", label_visibility="collapsed")
            
            st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
            
            # Link esqueceu senha (pequeno e roxo)
            col_link = st.columns([1])
            with col_link[0]:
                st.markdown('<div style="text-align: right;">', unsafe_allow_html=True)
                if st.button("Esqueceu a senha?", key="link_recuperar", use_container_width=False):
                    st.session_state.login_tab = 'register'
                    st.session_state.register_subtab = 'recuperar'
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
            
            if st.button("Entrar →", use_container_width=True, type="primary", key="btn_login"):
                if u and p:
                    r = db.verificar_login(u, p)
                    if r['status'] == 'success':
                        if r['approved']:
                            st.session_state.logged_in = True
                            st.session_state.role = r['role']
                            st.session_state.username = u
                            st.rerun()
                        else: 
                            st.warning("🔒 Seu acesso ainda está pendente.")
                    else: 
                        st.error(r['msg'])
                else:
                    st.error("Por favor, preencha todos os campos")
        
        # --- TELA DE REGISTRO ---
        else:
            
            # Sub-abas
            col_criar, col_recuperar = st.columns(2)
            
            with col_criar:
                if st.session_state.register_subtab == 'criar':
                    st.markdown('<div style="text-align: center; padding: 10px; border-bottom: 2px solid #ef4444; font-weight: 600; color: #0f172a; font-size: 14px;">Criar Conta</div>', unsafe_allow_html=True)
                else:
                    if st.button("Criar Conta", key="btn_criar_conta", use_container_width=True, type="secondary"):
                        st.session_state.register_subtab = 'criar'
                        st.rerun()
            
            with col_recuperar:
                if st.session_state.register_subtab == 'recuperar':
                    st.markdown('<div style="text-align: center; padding: 10px; border-bottom: 2px solid #ef4444; font-weight: 600; color: #0f172a; font-size: 14px;">Recuperar Senha</div>', unsafe_allow_html=True)
                else:
                    if st.button("Recuperar Senha", key="btn_recuperar_senha", use_container_width=True, type="secondary"):
                        st.session_state.register_subtab = 'recuperar'
                        st.session_state.recup_etapa = 0
                        st.rerun()
            
            st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
            
            if st.session_state.register_subtab == 'criar':
                # CRIAR CONTA
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<label style="font-size: 14px; font-weight: 500; color: #334155; display: block; margin-bottom: 0.5rem;">Novo Usuário</label>', unsafe_allow_html=True)
                    nu = st.text_input("novo_usuario", placeholder="Login", key="reg_u", label_visibility="collapsed")
                    
                with col2:
                    st.markdown('<label style="font-size: 14px; font-weight: 500; color: #334155; display: block; margin-bottom: 0.5rem;">E-mail</label>', unsafe_allow_html=True)
                    ne = st.text_input("novo_email", placeholder="seu@email.com", key="reg_e", label_visibility="collapsed")
                
                st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
                
                col3, col4 = st.columns(2)
                
                with col3:
                    st.markdown('<label style="font-size: 14px; font-weight: 500; color: #334155; display: block; margin-bottom: 0.5rem;">Senha</label>', unsafe_allow_html=True)
                    np = st.text_input("nova_senha", type="password", key="reg_p", label_visibility="collapsed")
                    
                with col4:
                    st.markdown('<label style="font-size: 14px; font-weight: 500; color: #334155; display: block; margin-bottom: 0.5rem;">Confirmar Senha</label>', unsafe_allow_html=True)
                    npc = st.text_input("confirmar_senha", type="password", key="reg_pc", label_visibility="collapsed")
                
                st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
                
                if st.button("Criar Minha Conta", use_container_width=True, type="primary", key="btn_criar"):
                    if np != npc: 
                        st.error("Senhas não conferem.")
                    elif not all([nu, ne, np, npc]):
                        st.error("Preencha todos os campos")
                    else:
                        res = db.registrar_usuario(nu, np, ne)
                        if res['status']:
                            st.success(f"Conta criada! ID: {res['id_gerado']}")
                            email_utils.email_boas_vindas(nu, ne)
                        else: 
                            st.error(res['msg'])
            
            else:
                # RECUPERAR SENHA
                
                if st.session_state.recup_etapa == 0:
                    st.info("Digite seu usuário e e-mail para receber o código de recuperação")
                    
                    st.markdown('<label style="font-size: 14px; font-weight: 500; color: #334155; display: block; margin-bottom: 0.5rem;">Seu Usuário</label>', unsafe_allow_html=True)
                    ru = st.text_input("recuperar_usuario", key="ru", label_visibility="collapsed")
                    
                    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
                    
                    st.markdown('<label style="font-size: 14px; font-weight: 500; color: #334155; display: block; margin-bottom: 0.5rem;">Seu E-mail</label>', unsafe_allow_html=True)
                    re = st.text_input("recuperar_email", key="re", label_visibility="collapsed")
                    
                    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
                    
                    if st.button("Enviar Código de Recuperação", use_container_width=True, type="primary", key="btn_enviar_codigo"):
                        if ru and re:
                            res = db.iniciar_recuperacao_senha(ru, re)
                            if res['status']:
                                email_utils.email_recuperacao(re, res['codigo'])
                                st.session_state.recup_etapa = 1
                                st.session_state.rec_user_temp = ru
                                st.success("Código enviado para seu e-mail!")
                                st.rerun()
                            else:
                                st.error(res['msg'])
                        else:
                            st.error("Preencha ambos os campos")
                
                else:
                    st.success("Código enviado! Verifique seu e-mail.")
                    
                    st.markdown('<label style="font-size: 14px; font-weight: 500; color: #334155; display: block; margin-bottom: 0.5rem;">Código recebido</label>', unsafe_allow_html=True)
                    rc = st.text_input("codigo_recuperacao", placeholder="Digite o código de 6 dígitos", label_visibility="collapsed", key="codigo_rec")
                    
                    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
                    
                    st.markdown('<label style="font-size: 14px; font-weight: 500; color: #334155; display: block; margin-bottom: 0.5rem;">Nova Senha</label>', unsafe_allow_html=True)
                    rn = st.text_input("nova_senha_recuperacao", type="password", placeholder="Nova senha", label_visibility="collapsed", key="nova_senha_rec")
                    
                    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("Voltar", use_container_width=True, type="secondary", key="btn_voltar_rec"):
                            st.session_state.recup_etapa = 0
                            st.rerun()
                    with col_btn2:
                        if st.button("Redefinir Senha", use_container_width=True, type="primary", key="btn_redefinir"):
                            if rc and rn:
                                if db.finalizar_recuperacao_senha(st.session_state.rec_user_temp, rc, rn):
                                    st.success("Senha atualizada com sucesso!")
                                    time.sleep(1.5)
                                    st.session_state.recup_etapa = 0
                                    st.session_state.login_tab = 'login'
                                    st.rerun()
                                else:
                                    st.error("Código inválido ou expirado")
                            else:
                                st.error("Preencha ambos os campos")

        # Footer
        st.markdown("""
        <div style="text-align: center; margin-top: 2.5rem; padding-top: 1.5rem; border-top: 1px solid #e2e8f0;">
            <p style="color: #94a3b8; font-size: 12px; margin: 0;">EDWCRED © 2024 • Sistema de Gestão</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# ÁREA LOGADA
# ==========================================
else:
    with st.sidebar:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px; padding: 12px; margin-bottom: 24px; border: 1px solid #f1f5f9; border-radius: 12px; background: #ffffff;">
            <div style="width: 40px; height: 40px; background: #f5f3ff; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #7c3aed; font-weight: 700;">
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

    if escolha == "🔒 Painel Admin":
        admin_panel.render_admin()
    else:
        mapa = {
            "📊 Dashboard": "Dashboard",
            "👥 Clientes": "Clientes",
            "➕ Novo Cadastro": "Novo Cadastro"
        }
        app_crm.render_page(mapa[escolha])