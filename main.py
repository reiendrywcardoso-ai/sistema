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
# CSS SUPREMO (Baseado no seu script Shadcn/React)
# ==========================================
st.markdown("""
    <style>
    /* 1. Fonte Inter */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #0f172a;
    }

    /* 2. Fundo Geral (Claro com Gradiente Suave) */
    .stApp {
        background-color: #f8fafc;
        background-image: radial-gradient(at 0% 0%, rgba(139, 92, 246, 0.15) 0px, transparent 50%), 
                          radial-gradient(at 100% 100%, rgba(124, 58, 237, 0.15) 0px, transparent 50%);
        background-attachment: fixed;
    }

    /* 3. Esconder elementos nativos */
    #MainMenu, footer, header {visibility: hidden;}

    /* 4. O CARTÃO DE LOGIN (Shadcn Style) */
    /* Aplicamos o estilo Shadcn no container com borda do Streamlit */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white;
        border: 1px solid #e2e8f0 !important;
        border-radius: 1rem !important; /* rounded-xl */
        padding: 2.5rem !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025);
        max-width: 450px;
        margin: auto;
    }
    
    /* Remove padding interno extra do container */
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        padding: 0 !important;
    }

    /* 5. Inputs (Campos de texto Clean) */
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

    /* 6. Botão Primário (Gradiente Violeta) */
    div.stButton > button[kind="primary"] {
        width: 100%;
        background: linear-gradient(to right, #8b5cf6, #7c3aed);
        color: white;
        border: none;
        height: 45px;
        border-radius: 0.5rem;
        font-weight: 500;
        font-size: 15px;
        box-shadow: 0 4px 6px -1px rgba(124, 58, 237, 0.3);
        margin-top: 10px;
    }
    div.stButton > button[kind="primary"]:hover {
        opacity: 0.9;
        transform: translateY(-1px);
        box-shadow: 0 6px 10px -1px rgba(124, 58, 237, 0.4);
        color: white;
    }

    /* 7. Botão Secundário */
    div.stButton > button[kind="secondary"] {
        background: white !important;
        color: #64748b !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1) !important;
        height: 40px;
    }
    div.stButton > button[kind="secondary"]:hover {
        background: #f8fafc !important;
        border-color: #cbd5e1 !important;
        color: #334155 !important;
    }

    /* 8. Sidebar Profissional */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
        box-shadow: 2px 0 10px rgba(0,0,0,0.01);
    }
    
    /* Menu Lateral */
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

    /* Labels e Textos */
    h1, h2, h3 { font-family: 'Inter', sans-serif; letter-spacing: -0.025em; }
    .custom-label {
        font-size: 14px; font-weight: 500; color: #334155; margin-bottom: 0.5rem; display: block;
    }
    
    /* Centralização Vertical na Coluna */
    div[data-testid="column"] { align-self: center; }

    </style>
""", unsafe_allow_html=True)

# ==========================================
# TELA DE LOGIN
# ==========================================
if not st.session_state.logged_in:
    
    st.write("")
    st.write("")
    
    # Colunas para centralizar o card
    col_esq, col_centro, col_dir = st.columns([1, 1.2, 1])
    
    with col_centro:
        # Usa o container com borda (que o CSS transforma no card Shadcn)
        with st.container(border=True):
            
            # Cabeçalho do Card
            st.markdown("""
            <div style="text-align: center; margin-bottom: 2rem;">
                <h1 style="font-size: 28px; font-weight: 700; color: #0f172a; margin-bottom: 0.5rem; letter-spacing: -0.025em;">Gestão Correspondente</h1>
                <p style="color: #64748b; font-size: 14px; margin: 0;">Sistema CRM para Correspondentes Bancários</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Abas de Navegação
            tab_login, tab_register = st.tabs(["Entrar", "Registar"])
            
            # --- ABA DE LOGIN ---
            with tab_login:
                st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
                
                st.markdown('<span class="custom-label">Utilizador</span>', unsafe_allow_html=True)
                u = st.text_input("utilizador_input", placeholder="Seu nome de utilizador", key="log_u", label_visibility="collapsed")
                
                st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
                
                st.markdown('<span class="custom-label">Senha</span>', unsafe_allow_html=True)
                p = st.text_input("senha_input", type="password", placeholder="••••••••••", key="log_p", label_visibility="collapsed")
                
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                
                # Link Esqueceu a senha
                if st.button("Esqueceu a senha?", key="link_recuperar"):
                    st.info("Acesse a aba 'Registar' > 'Recuperar Senha'")
                
                st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
                
                if st.button("Entrar →", use_container_width=True, type="primary"):
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

            # --- ABA DE REGISTRO ---
            with tab_register:
                st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
                
                sub_tab_novo, sub_tab_recuperar = st.tabs(["Criar Conta", "Recuperar Senha"])
                
                with sub_tab_novo:
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    
                    c_reg1, c_reg2 = st.columns(2)
                    with c_reg1:
                        st.markdown('<span class="custom-label">Usuário</span>', unsafe_allow_html=True)
                        nu = st.text_input("Novo Usuário", placeholder="Login", key="reg_u", label_visibility="collapsed")
                    with c_reg2:
                        st.markdown('<span class="custom-label">E-mail</span>', unsafe_allow_html=True)
                        ne = st.text_input("E-mail", placeholder="email@exemplo.com", key="reg_e", label_visibility="collapsed")
                    
                    c_reg3, c_reg4 = st.columns(2)
                    with c_reg3:
                        st.markdown('<span class="custom-label">Senha</span>', unsafe_allow_html=True)
                        np = st.text_input("Senha", type="password", key="reg_p", label_visibility="collapsed")
                    with c_reg4:
                        st.markdown('<span class="custom-label">Confirmar</span>', unsafe_allow_html=True)
                        npc = st.text_input("Confirmar Senha", type="password", key="reg_pc", label_visibility="collapsed")
                    
                    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
                    
                    if st.button("Criar Minha Conta", use_container_width=True, type="primary"):
                        if np != npc: st.error("Senhas não conferem.")
                        elif not all([nu, ne, np, npc]): st.error("Preencha todos os campos")
                        else:
                            res = db.registrar_usuario(nu, np, ne)
                            if res['status']:
                                st.success(f"Conta criada! ID: {res['id_gerado']}")
                                email_utils.email_boas_vindas(nu, ne)
                            else: st.error(res['msg'])
                
                with sub_tab_recuperar:
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    
                    if st.session_state.recup_etapa == 0:
                        st.info("Digite seus dados para receber o código.")
                        ru = st.text_input("Seu Usuário", key="ru")
                        re = st.text_input("Seu E-mail", key="re")
                        if st.button("Enviar Código", use_container_width=True, type="primary"):
                            if ru and re:
                                res = db.iniciar_recuperacao_senha(ru, re)
                                if res['status']:
                                    email_utils.email_recuperacao(re, res['codigo'])
                                    st.session_state.recup_etapa = 1
                                    st.session_state.rec_user_temp = ru
                                    st.success("Código enviado!")
                                else: st.error(res['msg'])
                            else: st.error("Preencha os campos")
                            
                    elif st.session_state.recup_etapa == 1:
                        st.success("Verifique seu e-mail.")
                        rc = st.text_input("Código", placeholder="123456")
                        rn = st.text_input("Nova Senha", type="password")
                        
                        c_b1, c_b2 = st.columns(2)
                        if c_b1.button("Voltar", use_container_width=True):
                            st.session_state.recup_etapa = 0; st.rerun()
                        if c_b2.button("Alterar Senha", use_container_width=True, type="primary"):
                            if db.finalizar_recuperacao_senha(st.session_state.rec_user_temp, rc, rn):
                                st.success("Senha atualizada!"); time.sleep(2)
                                st.session_state.recup_etapa = 0; st.rerun()
                            else: st.error("Erro ou código inválido.")

            # Rodapé (Ano 2026)
            st.markdown("""
            <div style="text-align: center; margin-top: 2.5rem; padding-top: 1.5rem; border-top: 1px solid #e2e8f0;">
                <p style="color: #94a3b8; font-size: 12px; margin: 0;">EDWCRED © 2026 • Sistema de Gestão</p>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# ÁREA LOGADA (SISTEMA)
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
