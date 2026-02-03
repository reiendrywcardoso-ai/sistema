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
        color: #0f172a; /* Slate-900 */
    }

    /* 2. Fundo Geral (Slate-50) */
    .stApp {
        background-color: #f8fafc;
        background-image: radial-gradient(at 0% 0%, rgba(139, 92, 246, 0.15) 0px, transparent 50%), 
                          radial-gradient(at 100% 100%, rgba(124, 58, 237, 0.15) 0px, transparent 50%);
        background-attachment: fixed;
    }

    /* 3. Esconder elementos nativos feios */
    #MainMenu, footer, header {visibility: hidden;}

    /* 4. Sidebar Estilo Dashboard Profissional */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0; /* Slate-200 */
        box-shadow: 2px 0 10px rgba(0,0,0,0.01);
    }

    /* 5. Menu Lateral (Links sem bolinhas) */
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label > div:first-child { display: none; }
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label {
        background-color: transparent;
        padding: 10px 14px;
        border-radius: 8px;
        margin-bottom: 4px;
        color: #64748b; /* Slate-500 */
        font-weight: 500;
        border: 1px solid transparent;
        transition: all 0.2s;
    }
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:hover {
        background-color: #f1f5f9;
        color: #7c3aed;
    }
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #f5f3ff; /* Violet-50 */
        color: #7c3aed; /* Violet-600 */
        font-weight: 600;
        border: 1px solid #ddd6fe;
    }

    /* 6. ESTILO DO CARTÃO DE LOGIN (REPLICAÇÃO DO SHADCN CARD) */
    .shadcn-card {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-radius: 1rem; /* rounded-xl */
        padding: 2.5rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025); /* shadow-lg */
        max-width: 100%;
    }

    /* 7. Inputs (Campos de texto) */
    .stTextInput input {
        height: 45px;
        border-radius: 0.5rem; /* rounded-lg */
        border: 1px solid #e2e8f0;
        padding: 0 12px;
        font-size: 14px;
        color: #1e293b;
        background-color: white;
        transition: all 0.2s;
    }
    .stTextInput input:focus {
        border-color: #8b5cf6; /* Violet-500 */
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2); /* Ring-2 ring-violet */
    }

    /* 8. Botão Primário (Gradiente Violeta - Igual ao Lovable) */
    .stButton > button {
        width: 100%;
        background: linear-gradient(to right, #8b5cf6, #7c3aed); /* Violet-500 -> 600 */
        color: white;
        border: none;
        height: 45px;
        border-radius: 0.5rem;
        font-weight: 500;
        font-size: 15px;
        box-shadow: 0 4px 6px -1px rgba(124, 58, 237, 0.3);
        transition: transform 0.1s;
    }
    .stButton > button:hover {
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
    }
    .stButton > button[kind="secondary"]:hover {
        background: #f8fafc !important;
        border-color: #cbd5e1 !important;
        color: #334155 !important;
    }

    /* 10. Abas (Tabs) Clean */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 20px;
        padding-bottom: 0px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        background: transparent;
        border: none;
        color: #64748b;
        font-weight: 500;
        padding: 0 10px;
    }
    .stTabs [aria-selected="true"] {
        background: transparent !important;
        color: #7c3aed !important;
        border-bottom: 2px solid #7c3aed;
    }

    /* Títulos e Textos */
    h1, h2, h3 { font-family: 'Inter', sans-serif; letter-spacing: -0.025em; }
    
    /* Centralizar conteúdo verticalmente no login */
    div[data-testid="stVerticalBlock"] { gap: 0rem; }
    
    /* Link estilo texto */
    .link-texto {
        color: #64748b;
        font-size: 13px;
        text-decoration: none;
        cursor: pointer;
        transition: color 0.2s;
    }
    .link-texto:hover {
        color: #7c3aed;
    }
    </style>
""", unsafe_allow_html=True)

# --- Sessão ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'role' not in st.session_state: st.session_state.role = ''
if 'username' not in st.session_state: st.session_state.username = ''
if 'recup_etapa' not in st.session_state: st.session_state.recup_etapa = 0
if 'login_tab' not in st.session_state: st.session_state.login_tab = 'login'

# ==========================================
# TELA DE LOGIN (IGUAL À IMAGEM)
# ==========================================
if not st.session_state.logged_in:
    
    # Layout de colunas para centralizar o card perfeitamente
    # [Espaço] [CARD] [Espaço]
    col_esq, col_centro, col_dir = st.columns([1, 1.2, 1])
    
    with col_centro:
        # Espaçamento do topo
        st.write("") 
        st.write("") 
        
        # INÍCIO DO CARD HTML
        # INÍCIO DO CARD HTML
        st.markdown('<div class="shadcn-card">', unsafe_allow_html=True)
        
        # Cabeçalho do Card (com ícone igual à imagem)
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="width: 72px; height: 72px; background: linear-gradient(135deg, #8b5cf6, #7c3aed); border-radius: 16px; display: inline-flex; align-items: center; justify-content: center; margin: 0 auto 1.5rem auto; box-shadow: 0 4px 6px -1px rgba(124, 58, 237, 0.2);">
                <span style="font-size: 36px;">📱</span>
            </div>
            <h1 style="font-size: 28px; font-weight: 700; color: #0f172a; margin-bottom: 0.5rem; letter-spacing: -0.025em;">Gestão Correspondente</h1>
            <p style="color: #64748b; font-size: 14px; margin: 0;">Sistema CRM para Correspondentes Bancários</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Botões Entrar / Registar (igual à imagem)
        col_entrar, col_registar = st.columns(2)
        
        with col_entrar:
            if st.session_state.login_tab == 'login':
                st.markdown("""
                <div style="text-align: center; padding: 14px; background: white; border-bottom: 2px solid #7c3aed; 
                            font-weight: 600; color: #0f172a; cursor: pointer; font-size: 15px;">
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
                <div style="text-align: center; padding: 14px; background: white; border-bottom: 2px solid #7c3aed; 
                            font-weight: 600; color: #0f172a; cursor: pointer; font-size: 15px;">
                    Registar
                </div>
                """, unsafe_allow_html=True)
            else:
                if st.button("Registar", key="btn_registar", use_container_width=True, type="secondary"):
                    st.session_state.login_tab = 'register'
                    st.rerun()
        
        st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)
        
        # --- CONTEÚDO BASEADO NA SELEÇÃO ---
        if st.session_state.login_tab == 'login':
            # --- TELA DE LOGIN ---
            
            # Label do campo Utilizador com ícone
            st.markdown("""
            <div style="margin-bottom: 0.5rem;">
                <label style="font-size: 14px; font-weight: 500; color: #334155;">Utilizador</label>
            </div>
            """, unsafe_allow_html=True)
            
            # Campo de usuário com ícone
            col_icon_user, col_input_user = st.columns([0.1, 0.9])
            with col_icon_user:
                st.markdown('<div style="padding-top: 12px; font-size: 20px;">👤</div>', unsafe_allow_html=True)
            with col_input_user:
                u = st.text_input("utilizador_input", 
                                 placeholder="Seu nome de utilizador", 
                                 key="log_u", 
                                 label_visibility="collapsed")
            
            # Espaço entre campos
            st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
            
            # Label do campo Senha com ícone
            st.markdown("""
            <div style="margin-bottom: 0.5rem;">
                <label style="font-size: 14px; font-weight: 500; color: #334155;">Senha</label>
            </div>
            """, unsafe_allow_html=True)
            
            # Campo de senha com ícone
            col_icon_pass, col_input_pass = st.columns([0.1, 0.9])
            with col_icon_pass:
                st.markdown('<div style="padding-top: 12px; font-size: 20px;">🔒</div>', unsafe_allow_html=True)
            with col_input_pass:
                p = st.text_input("senha_input", 
                                 type="password", 
                                 placeholder="••••••••", 
                                 key="log_p", 
                                 label_visibility="collapsed")
            
            # Link "Esqueceu a senha?" (como na imagem)
            st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)
            st.markdown("""
            <div style="text-align: right;">
                <a href="#" style="color: #8b5cf6; font-size: 13px; text-decoration: none; font-weight: 500;">
                    Esqueceu a senha?
                </a>
            </div>
            """, unsafe_allow_html=True)
            
            # Botão de login principal
            st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
            if st.button("Entrar →", use_container_width=True, type="primary"):
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
        
        else:
            # --- TELA DE REGISTRO ---
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            
            # Sub-aba para escolher entre registro ou recuperação
            sub_tab_novo, sub_tab_recuperar = st.tabs(["Criar Conta", "Recuperar Senha"])
            
            with sub_tab_novo:
                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                
                c_reg1, c_reg2 = st.columns(2)
                nu = c_reg1.text_input("Novo Usuário", placeholder="Login", key="reg_u")
                ne = c_reg2.text_input("E-mail", placeholder="seu@email.com", key="reg_e")
                np = c_reg1.text_input("Senha", type="password", key="reg_p")
                npc = c_reg2.text_input("Confirmar Senha", type="password", key="reg_pc")
                
                st.write("")
                if st.button("Criar Minha Conta", use_container_width=True):
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
            
            with sub_tab_recuperar:
                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                
                if st.session_state.recup_etapa == 0:
                    st.info("Digite seu usuário e e-mail para receber o código de recuperação")
                    ru = st.text_input("Seu Usuário", key="ru")
                    re = st.text_input("Seu E-mail", key="re")
                    
                    if st.button("Enviar Código de Recuperação", use_container_width=True):
                        if ru and re:
                            res = db.iniciar_recuperacao_senha(ru, re)
                            if res['status']:
                                email_utils.email_recuperacao(re, res['codigo'])
                                st.session_state.recup_etapa = 1
                                st.session_state.rec_user_temp = ru
                                st.success("Código enviado para seu e-mail!")
                            else:
                                st.error(res['msg'])
                        else:
                            st.error("Preencha ambos os campos")
                
                elif st.session_state.recup_etapa == 1:
                    st.success("Código enviado! Verifique seu e-mail.")
                    rc = st.text_input("Código recebido", placeholder="Digite o código de 6 dígitos")
                    rn = st.text_input("Nova Senha", type="password", placeholder="Nova senha")
                    
                    col_btn_rec = st.columns(2)
                    with col_btn_rec[0]:
                        if st.button("Voltar", use_container_width=True):
                            st.session_state.recup_etapa = 0
                            st.rerun()
                    with col_btn_rec[1]:
                        if st.button("Redefinir Senha", use_container_width=True, type="primary"):
                            if rc and rn:
                                if db.finalizar_recuperacao_senha(st.session_state.rec_user_temp, rc, rn):
                                    st.success("Senha atualizada com sucesso!")
                                    time.sleep(2)
                                    st.session_state.recup_etapa = 0
                                    st.rerun()
                                else:
                                    st.error("Código inválido ou expirado")
                            else:
                                st.error("Preencha ambos os campos")

        # Footer (exatamente como na imagem)
        st.markdown("""
        <div style="text-align: center; margin-top: 2.5rem; padding-top: 1.5rem; border-top: 1px solid #e2e8f0;">
            <p style="color: #94a3b8; font-size: 12px; margin: 0;">EDWCRED © 2024 • Sistema de Gestão</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True) # Fim do Card

# ==========================================
# ÁREA LOGADA (SISTEMA)
# ==========================================
else:
    # Sidebar
    with st.sidebar:
        # Card de Perfil Minimalista
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
        
        # --- DEFINIÇÃO DO MENU ---
        opcoes_menu = ["📊 Dashboard", "👥 Clientes", "➕ Novo Cadastro"]
        
        if st.session_state.role == 'admin':
            opcoes_menu.append("🔒 Painel Admin")
            
        escolha = st.radio("Navegação", opcoes_menu, label_visibility="collapsed")
            
        st.markdown("---")
        if st.button("Sair", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # --- ROTEAMENTO DE PÁGINAS ---
    # Aqui está a correção: mapeamos os nomes do menu para os argumentos esperados pela função
    if escolha == "🔒 Painel Admin":
        admin_panel.render_admin()
    else:
        # Mapeamento para o app_crm
        mapa = {
            "📊 Dashboard": "Dashboard",
            "👥 Clientes": "Clientes",
            "➕ Novo Cadastro": "Novo Cadastro"
        }
        # Chama a função principal do CRM passando a página correta
        app_crm.render_page(mapa[escolha])