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

# --- CSS SUPREMO (Correção Definitiva do Card) ---
st.markdown("""
    <style>
    /* 1. Fonte Inter */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * {
        font-family: 'Inter', sans-serif;
    }

    /* 2. Fundo Geral (Gradiente Roxo) */
    .stApp {
        background: linear-gradient(135deg, #8A56E8 0%, #7A4FE3 100%);
    }

    /* 3. Esconder elementos nativos */
    #MainMenu, footer, header {visibility: hidden;}

    /* 4. O "QUADRADO" (Card de Login) 
       Agora miramos no container com borda que criamos no Python.
       Isso garante que o fundo pegue todo o formulário. */
    
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #F3EFFE; /* Lilás bem claro (Fundo do Card) */
        border-radius: 24px;
        padding: 2rem !important; /* Espaçamento interno */
        box-shadow: 0 20px 50px rgba(0,0,0,0.15); /* Sombra suave */
        border: 1px solid rgba(255,255,255,0.5) !important;
        margin-top: 2rem;
    }
    
    /* Remove o padding padrão extra do container interno para ficar alinhado */
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        padding: 0 !important;
    }

    /* 5. Inputs Estilizados */
    div[data-baseweb="input"] {
        background-color: #EBE5F5 !important; /* Fundo cinza/lilás do input */
        border: none !important;
        border-radius: 12px !important;
        padding: 8px;
    }
    div[data-baseweb="base-input"] {
        background-color: transparent !important;
    }
    input.stTextInput {
        background-color: transparent !important;
        color: #1e293b !important;
        font-weight: 500;
    }
    /* Esconde o label padrão */
    .stTextInput label {
        display: none;
    }

    /* 6. Botão Primário (Entrar) */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #7A4FE3 0%, #6d28d9 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        height: 55px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        width: 100% !important;
        transition: all 0.2s ease;
        box-shadow: 0 4px 15px rgba(122, 79, 227, 0.4);
        margin-top: 10px;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(122, 79, 227, 0.6);
    }

    /* 7. Botão Secundário (Abas/Links) */
    div.stButton > button[kind="secondary"] {
        background-color: transparent !important;
        border: none !important;
        color: #64748b !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        height: 40px !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        color: #7A4FE3 !important;
        background-color: rgba(122, 79, 227, 0.1) !important;
    }

    /* 8. Labels Customizados */
    .custom-label {
        color: #475569;
        font-weight: 600;
        font-size: 13px;
        margin-bottom: 8px;
        display: block;
        margin-top: 8px;
    }

    /* 9. Sidebar Customizada */
    section[data-testid="stSidebar"] {
        background-color: white;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Centralização na tela */
    div[data-testid="column"] {
        align-self: center;
    }
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
    
    st.write("") 
    st.write("") 
    
    # Colunas para centralizar
    col_vazia_esq, col_login, col_vazia_dir = st.columns([1, 1.2, 1])
    
    with col_login:
        # AQUI ESTÁ A MÁGICA: st.container(border=True)
        # O CSS "stVerticalBlockBorderWrapper" vai estilizar exatamente este bloco
        with st.container(border=True):
            
            # 1. Ícone do Topo
            st.markdown("""
                <div style="display: flex; justify-content: center; margin-bottom: 20px; margin-top: 10px;">
                    <div style="width: 64px; height: 64px; background-color: #7A4FE3; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 30px; box-shadow: 0 10px 20px rgba(122, 79, 227, 0.3);">
                        📄
                    </div>
                </div>
                <div style="text-align: center; margin-bottom: 30px;">
                    <h2 style="margin: 0; color: #1e293b; font-weight: 800; font-size: 24px;">Gestão Correspondente</h2>
                    <p style="margin: 6px 0 0 0; color: #64748b; font-size: 13px;">Sistema CRM para Correspondentes Bancários</p>
                </div>
            """, unsafe_allow_html=True)

            # 2. Abas (Simulando Segmented Button)
            st.markdown('<div style="background-color: #E6E0F5; padding: 4px; border-radius: 12px; margin-bottom: 25px;">', unsafe_allow_html=True)
            c_tab1, c_tab2 = st.columns(2)
            with c_tab1:
                if st.session_state.login_tab == 'login':
                    st.markdown('<div style="background: white; border-radius: 10px; text-align: center; padding: 10px; color: #7A4FE3; font-weight: 700; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); cursor: default;">Entrar</div>', unsafe_allow_html=True)
                else:
                    if st.button("Entrar", key="tab_entrar", use_container_width=True, type="secondary"):
                        st.session_state.login_tab = 'login'
                        st.rerun()
            with c_tab2:
                if st.session_state.login_tab == 'register':
                    st.markdown('<div style="background: white; border-radius: 10px; text-align: center; padding: 10px; color: #7A4FE3; font-weight: 700; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); cursor: default;">Registar</div>', unsafe_allow_html=True)
                else:
                    if st.button("Registar", key="tab_registrar", use_container_width=True, type="secondary"):
                        st.session_state.login_tab = 'register'
                        st.session_state.register_subtab = 'criar'
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

            # --- LOGIN ---
            if st.session_state.login_tab == 'login':
                
                st.markdown('<span class="custom-label">Utilizador</span>', unsafe_allow_html=True)
                col_ico1, col_inp1 = st.columns([0.15, 0.85])
                with col_ico1:
                    st.markdown('<div style="height: 44px; background: #EBE5F5; border-radius: 12px 0 0 12px; display: flex; align-items: center; justify-content: center; font-size: 18px; color: #7A4FE3;">👤</div>', unsafe_allow_html=True)
                with col_inp1:
                    st.markdown('<style>div[data-testid="stTextInput"] { margin-left: -15px; }</style>', unsafe_allow_html=True)
                    u = st.text_input("user_login", placeholder="Seu nome de utilizador", label_visibility="collapsed")

                st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)

                st.markdown('<span class="custom-label">Senha</span>', unsafe_allow_html=True)
                col_ico2, col_inp2 = st.columns([0.15, 0.85])
                with col_ico2:
                    st.markdown('<div style="height: 44px; background: #EBE5F5; border-radius: 12px 0 0 12px; display: flex; align-items: center; justify-content: center; font-size: 18px; color: #7A4FE3;">🔒</div>', unsafe_allow_html=True)
                with col_inp2:
                    p = st.text_input("pass_login", type="password", placeholder="••••••••", label_visibility="collapsed")

                st.markdown('<div style="text-align: right; margin-top: 8px; margin-bottom: 24px;">', unsafe_allow_html=True)
                if st.button("Esqueceu a senha?", key="link_recuperar_top", type="secondary"):
                    st.session_state.login_tab = 'register'
                    st.session_state.register_subtab = 'recuperar'
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

                if st.button("Entrar   →", type="primary", use_container_width=True):
                    if u and p:
                        r = db.verificar_login(u, p)
                        if r['status'] == 'success':
                            if r['approved']:
                                st.session_state.logged_in = True
                                st.session_state.role = r['role']
                                st.session_state.username = u
                                st.rerun()
                            else: st.warning("🔒 Aguardando aprovação.")
                        else: st.error(r['msg'])
                    else: st.warning("Preencha todos os campos.")

            # --- REGISTRO / RECUPERAÇÃO ---
            else:
                if st.session_state.register_subtab == 'criar':
                    st.markdown('<span class="custom-label">Novo Usuário</span>', unsafe_allow_html=True)
                    nu = st.text_input("reg_user", placeholder="Escolha um login", label_visibility="collapsed")
                    
                    st.markdown('<span class="custom-label">E-mail</span>', unsafe_allow_html=True)
                    ne = st.text_input("reg_email", placeholder="seu@email.com", label_visibility="collapsed")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown('<span class="custom-label">Senha</span>', unsafe_allow_html=True)
                        np = st.text_input("reg_pass", type="password", label_visibility="collapsed")
                    with c2:
                        st.markdown('<span class="custom-label">Confirmar</span>', unsafe_allow_html=True)
                        npc = st.text_input("reg_pass_conf", type="password", label_visibility="collapsed")

                    st.markdown('<div style="height: 25px;"></div>', unsafe_allow_html=True)

                    if st.button("Criar Conta", type="primary", use_container_width=True):
                        if np != npc: st.error("Senhas não conferem.")
                        elif not all([nu, ne, np, npc]): st.error("Preencha tudo.")
                        else:
                            res = db.registrar_usuario(nu, np, ne)
                            if res['status']:
                                st.success(f"Conta criada! ID: {res['id_gerado']}")
                                email_utils.email_boas_vindas(nu, ne)
                            else: st.error(res['msg'])
                    
                    st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
                    if st.button("Já tenho conta", type="secondary", use_container_width=True):
                        st.session_state.login_tab = 'login'
                        st.rerun()

                elif st.session_state.register_subtab == 'recuperar':
                    st.markdown("<h4 style='color: #475569; text-align: center;'>Recuperar Senha</h4>", unsafe_allow_html=True)
                    if st.session_state.recup_etapa == 0:
                        st.markdown('<span class="custom-label">Usuário</span>', unsafe_allow_html=True)
                        ru = st.text_input("rec_user", label_visibility="collapsed")
                        st.markdown('<span class="custom-label">E-mail</span>', unsafe_allow_html=True)
                        re = st.text_input("rec_email", label_visibility="collapsed")
                        
                        st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
                        if st.button("Enviar Código", type="primary", use_container_width=True):
                            res = db.iniciar_recuperacao_senha(ru, re)
                            if res['status']:
                                email_utils.email_recuperacao(re, res['codigo'])
                                st.session_state.recup_etapa = 1
                                st.session_state.rec_user_temp = ru
                                st.success("Verifique seu e-mail!")
                                time.sleep(1); st.rerun()
                            else: st.error(res['msg'])
                    else:
                        st.info("Código enviado!")
                        rc = st.text_input("Código", placeholder="123456")
                        rn = st.text_input("Nova Senha", type="password")
                        if st.button("Alterar Senha", type="primary", use_container_width=True):
                            if db.finalizar_recuperacao_senha(st.session_state.rec_user_temp, rc, rn):
                                st.success("Sucesso! Faça login."); time.sleep(1)
                                st.session_state.login_tab = 'login'; st.session_state.recup_etapa = 0; st.rerun()
                            else: st.error("Erro ao alterar.")
                    
                    st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
                    if st.button("Voltar", type="secondary", use_container_width=True):
                        st.session_state.login_tab = 'login'; st.session_state.register_subtab = 'criar'; st.rerun()

            st.markdown("""
                <div style="text-align: center; margin-top: 30px; color: #94a3b8; font-size: 11px;">
                    EDWCRED © 2024 • Sistema de Gestão
                </div>
            """, unsafe_allow_html=True)

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
        if st.session_state.role == 'admin': opcoes_menu.append("🔒 Painel Admin")
            
        escolha = st.radio("Navegação", opcoes_menu, label_visibility="collapsed")
            
        st.markdown("---")
        if st.button("Sair", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    if escolha == "🔒 Painel Admin": admin_panel.render_admin()
    else:
        mapa = {"📊 Dashboard": "Dashboard", "👥 Clientes": "Clientes", "➕ Novo Cadastro": "Novo Cadastro"}
        app_crm.render_page(mapa[escolha])