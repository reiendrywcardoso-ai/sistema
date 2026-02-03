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

# --- CSS SUPREMO (Correção do Card "Quadrado") ---
st.markdown("""
    <style>
    /* 1. Fonte Inter */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * {
        font-family: 'Inter', sans-serif;
    }

    /* 2. Fundo Geral (Roxo Sólido/Gradiente) */
    .stApp {
        background: linear-gradient(135deg, #8A56E8 0%, #7A4FE3 100%);
    }

    /* 3. Esconder elementos nativos */
    #MainMenu, footer, header {visibility: hidden;}

    /* 4. O "QUADRADO" (Card de Login) 
       Aqui está o segredo: aplicamos o estilo diretamente na coluna do meio do Streamlit */
    
    div[data-testid="column"]:nth-of-type(2) > div[data-testid="stVerticalBlock"] {
        background-color: #F3EFFE; /* Lilás bem claro (Card) */
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        border: 1px solid rgba(255,255,255,0.4);
    }

    /* Ajuste para telas pequenas (Mobile) - removemos o card fixo se empilhar */
    @media (max-width: 640px) {
        div[data-testid="column"]:nth-of-type(2) > div[data-testid="stVerticalBlock"] {
            background-color: transparent;
            box-shadow: none;
            border: none;
            padding: 10px;
        }
    }

    /* 5. Inputs Estilizados */
    div[data-baseweb="input"] {
        background-color: #EBE5F5 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 5px;
    }
    div[data-baseweb="base-input"] {
        background-color: transparent !important;
    }
    input.stTextInput {
        background-color: transparent !important;
        color: #333 !important;
    }
    /* Esconde o label padrão */
    .stTextInput label {
        display: none;
    }

    /* 6. Botão Primário (Roxo forte) */
    div.stButton > button[kind="primary"] {
        background-color: #7A4FE3 !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        height: 50px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        width: 100% !important;
        transition: all 0.2s ease;
        box-shadow: 0 4px 15px rgba(122, 79, 227, 0.4);
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #673FD0 !important;
        transform: translateY(-2px);
    }

    /* 7. Botão Secundário (Abas/Links) */
    div.stButton > button[kind="secondary"] {
        background-color: transparent !important;
        border: none !important;
        color: #7A7A7A !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        color: #7A4FE3 !important;
        background-color: rgba(122, 79, 227, 0.1) !important;
    }

    /* 8. Labels Customizados */
    .custom-label {
        color: #333;
        font-weight: 600;
        font-size: 13px;
        margin-bottom: 6px;
        display: block;
    }

    /* 9. Sidebar Customizada (Apenas área logada) */
    section[data-testid="stSidebar"] {
        background-color: white;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Centralização vertical */
    div[data-testid="stVerticalBlock"] > div:has(div[data-testid="column"]) {
        align-items: center;
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
    
    st.write("") # Espaçamento topo
    st.write("") 
    
    # Layout de colunas para centralizar o CARD
    # O CSS acima (item 4) vai pegar especificamente essa col_login (2ª coluna) e transformá-la no card
    col_vazia_esq, col_login, col_vazia_dir = st.columns([1, 1.2, 1])
    
    with col_login:
        
        # --- CONTEÚDO DO CARD ---
        
        # 1. Ícone do Topo
        st.markdown("""
            <div style="display: flex; justify-content: center; margin-bottom: 20px;">
                <div style="width: 60px; height: 60px; background-color: #7A4FE3; border-radius: 15px; display: flex; align-items: center; justify-content: center; font-size: 28px; box-shadow: 0 10px 20px rgba(122, 79, 227, 0.3);">
                    📄
                </div>
            </div>
            <div style="text-align: center; margin-bottom: 30px;">
                <h2 style="margin: 0; color: #1A1A1A; font-weight: 700; font-size: 24px;">Gestão Correspondente</h2>
                <p style="margin: 5px 0 0 0; color: #7A7A7A; font-size: 13px;">Sistema CRM para Correspondentes Bancários</p>
            </div>
        """, unsafe_allow_html=True)

        # 2. Abas (Simulando Segmented Button)
        st.markdown('<div style="background-color: #E6E0F5; padding: 4px; border-radius: 12px; margin-bottom: 25px;">', unsafe_allow_html=True)
        c_tab1, c_tab2 = st.columns(2)
        with c_tab1:
            if st.session_state.login_tab == 'login':
                st.markdown('<div style="background: white; border-radius: 10px; text-align: center; padding: 10px; color: #7A4FE3; font-weight: bold; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); cursor: default;">Entrar</div>', unsafe_allow_html=True)
            else:
                if st.button("Entrar", key="tab_entrar", use_container_width=True, type="secondary"):
                    st.session_state.login_tab = 'login'
                    st.rerun()
        with c_tab2:
            if st.session_state.login_tab == 'register':
                st.markdown('<div style="background: white; border-radius: 10px; text-align: center; padding: 10px; color: #7A4FE3; font-weight: bold; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); cursor: default;">Registar</div>', unsafe_allow_html=True)
            else:
                if st.button("Registar", key="tab_registrar", use_container_width=True, type="secondary"):
                    st.session_state.login_tab = 'register'
                    st.session_state.register_subtab = 'criar'
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # --- LOGIN ---
        if st.session_state.login_tab == 'login':
            
            st.markdown('<span class="custom-label">Utilizador</span>', unsafe_allow_html=True)
            # Layout Ícone + Input
            col_ico1, col_inp1 = st.columns([0.15, 0.85])
            with col_ico1:
                st.markdown('<div style="height: 44px; background: #EBE5F5; border-radius: 10px 0 0 10px; display: flex; align-items: center; justify-content: center; font-size: 18px;">👤</div>', unsafe_allow_html=True)
            with col_inp1:
                st.markdown('<style>div[data-testid="stTextInput"] { margin-left: -15px; }</style>', unsafe_allow_html=True)
                u = st.text_input("user_login", placeholder="Seu nome de utilizador", label_visibility="collapsed")

            st.markdown('<div style="height: 15px;"></div>', unsafe_allow_html=True)

            st.markdown('<span class="custom-label">Senha</span>', unsafe_allow_html=True)
            col_ico2, col_inp2 = st.columns([0.15, 0.85])
            with col_ico2:
                st.markdown('<div style="height: 44px; background: #EBE5F5; border-radius: 10px 0 0 10px; display: flex; align-items: center; justify-content: center; font-size: 18px;">🔒</div>', unsafe_allow_html=True)
            with col_inp2:
                p = st.text_input("pass_login", type="password", placeholder="••••••••", label_visibility="collapsed")

            st.markdown('<div style="text-align: right; margin-top: 5px; margin-bottom: 20px;">', unsafe_allow_html=True)
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
                
                st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
                
                st.markdown('<span class="custom-label">E-mail</span>', unsafe_allow_html=True)
                ne = st.text_input("reg_email", placeholder="seu@email.com", label_visibility="collapsed")
                
                st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown('<span class="custom-label">Senha</span>', unsafe_allow_html=True)
                    np = st.text_input("reg_pass", type="password", label_visibility="collapsed")
                with c2:
                    st.markdown('<span class="custom-label">Confirmar</span>', unsafe_allow_html=True)
                    npc = st.text_input("reg_pass_conf", type="password", label_visibility="collapsed")

                st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

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
                st.markdown("##### Recuperar Senha")
                if st.session_state.recup_etapa == 0:
                    st.markdown('<span class="custom-label">Usuário</span>', unsafe_allow_html=True)
                    ru = st.text_input("rec_user", label_visibility="collapsed")
                    st.markdown('<span class="custom-label">E-mail</span>', unsafe_allow_html=True)
                    re = st.text_input("rec_email", label_visibility="collapsed")
                    
                    st.markdown('<div style="height: 15px;"></div>', unsafe_allow_html=True)
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
                
                if st.button("Voltar", type="secondary"):
                    st.session_state.login_tab = 'login'; st.session_state.register_subtab = 'criar'; st.rerun()

        st.markdown("""
            <div style="text-align: center; margin-top: 30px; color: #999; font-size: 11px;">
                EDWCRED © 2024 • Sistema de Gestão
            </div>
        """, unsafe_allow_html=True)

# ==========================================
# ÁREA LOGADA
# ==========================================
else:
    # 9. Sidebar Customizada (CSS remove o fundo roxo da sidebar se vazar)
    # Mas aqui definimos o conteúdo
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