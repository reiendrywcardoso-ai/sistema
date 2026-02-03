import streamlit as st
import database as db
import app_crm
import admin_panel
import email_utils
import time

# --- Configuração Global ---
st.set_page_config(page_title="Gestão Correspondente", layout="wide", page_icon="🟣")
db.init_db()

# --- CSS GLOBAL (Visual React/Lovable + Sidebar Menu) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1e293b;
    }

    .stApp {
        background-color: #f8fafc;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }

    /* ESTILO DO MENU LATERAL (Remover bolinhas do radio) */
    section[data-testid="stSidebar"] .stRadio > div {
        gap: 10px;
    }
    
    section[data-testid="stSidebar"] .stRadio label {
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 0.5rem;
        padding: 10px 15px;
        color: #64748b;
        font-weight: 500;
        transition: all 0.2s;
        cursor: pointer;
    }

    /* Item selecionado no menu */
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #f3e8ff; /* Fundo Roxo Claro */
        color: #7c3aed; /* Texto Roxo */
        border: 1px solid #d8b4fe;
        font-weight: 600;
    }

    /* Hover no menu */
    section[data-testid="stSidebar"] .stRadio label:hover {
        background-color: #f8fafc;
        color: #7c3aed;
    }

    /* Esconde a bolinha do radio button */
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label div:first-child {
        display: none;
    }

    /* Cards e Botões */
    .dashboard-card {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-radius: 1rem;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    .stButton>button {
        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        font-weight: 600;
    }
    
    .login-glass {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: 1.5rem;
        padding: 3rem;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    }
    </style>
""", unsafe_allow_html=True)

# --- Sessão ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'role' not in st.session_state: st.session_state.role = ''
if 'username' not in st.session_state: st.session_state.username = ''
if 'recup_etapa' not in st.session_state: st.session_state.recup_etapa = 0

# --- LOGIN ---
if not st.session_state.logged_in:
    st.markdown("""<style>.stApp {background: radial-gradient(circle at top left, #a78bfa, #7c3aed, #4c1d95);}</style>""", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.write(""); st.write("")
        st.markdown('<div class="login-glass">', unsafe_allow_html=True)
        st.markdown("""<div style="display: flex; justify-content: center; margin-bottom: 20px;"><div style="background: linear-gradient(135deg, #8b5cf6, #6d28d9); width: 64px; height: 64px; border-radius: 16px; display: flex; align-items: center; justify-content: center; color: white; font-size: 32px; box-shadow: 0 10px 15px -3px rgba(124, 58, 237, 0.3);">🏦</div></div>""", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>Gestão Correspondente</h2>", unsafe_allow_html=True)
        
        tab_login, tab_register = st.tabs(["Entrar", "Criar Conta"])
        with tab_login:
            u = st.text_input("Usuário", key="log_u")
            p = st.text_input("Senha", type="password", key="log_p")
            st.write("")
            if st.button("ACESSAR SISTEMA", use_container_width=True):
                r = db.verificar_login(u, p)
                if r['status'] == 'success':
                    if r['approved']:
                        st.session_state.logged_in = True
                        st.session_state.role = r['role']
                        st.session_state.username = u
                        st.rerun()
                    else: st.warning("🔒 Aguardando aprovação.")
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

        with tab_register:
            nu = st.text_input("Novo Usuário", key="reg_u"); ne = st.text_input("E-mail", key="reg_e")
            np = st.text_input("Senha", type="password", key="reg_p"); npc = st.text_input("Confirmar", type="password", key="reg_pc")
            if st.button("SOLICITAR ACESSO", use_container_width=True):
                if np != npc: st.error("Senhas não batem.")
                else:
                    res = db.registrar_usuario(nu, np, ne)
                    if res['status']: st.success(f"ID: {res['id_gerado']}"); email_utils.email_boas_vindas(nu, ne)
                    else: st.error(res['msg'])
        st.markdown('</div>', unsafe_allow_html=True)

# --- ÁREA INTERNA (MENU LATERAL UNIFICADO) ---
else:
    with st.sidebar:
        # Card de Perfil
        st.markdown(f"""
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; display: flex; align-items: center; gap: 12px; margin-bottom: 24px;">
            <div style="width: 38px; height: 38px; background: #f3e8ff; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #7c3aed; font-weight: 700;">
                {st.session_state.username[0].upper()}
            </div>
            <div>
                <div style="font-weight: 600; color: #0f172a; font-size: 14px;">{st.session_state.username}</div>
                <div style="color: #64748b; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">{st.session_state.role}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<p style='color: #94a3b8; font-size: 12px; font-weight: 600; padding-left: 5px; margin-bottom: 5px;'>MENU PRINCIPAL</p>", unsafe_allow_html=True)
        
        # --- DEFINIÇÃO DO MENU ---
        # Opções padrões para todos
        opcoes_menu = ["📊 Dashboard", "👥 Clientes", "➕ Novo Cadastro"]
        
        # Se for Admin, adiciona o painel
        if st.session_state.role == 'admin':
            opcoes_menu.append("🔒 Painel Admin")
            
        # O Seletor (Radio) que parece menu
        escolha = st.radio("Navegação", opcoes_menu, label_visibility="collapsed")
            
        st.markdown("---")
        if st.button("Sair", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # --- ROTEAMENTO DE PÁGINAS ---
    # Removemos o "render_crm" genérico e chamamos a função passando a página escolhida
    if escolha == "🔒 Painel Admin":
        admin_panel.render_admin()
    else:
        # Mapeia os nomes com emojis para os nomes técnicos
        pagina_map = {
            "📊 Dashboard": "Dashboard",
            "👥 Clientes": "Clientes",
            "➕ Novo Cadastro": "Novo Cadastro"
        }
        # Chama o app_crm passando qual página deve abrir
        app_crm.render_page(pagina_map[escolha])