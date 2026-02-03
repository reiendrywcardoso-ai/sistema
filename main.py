import streamlit as st
import database as db
import app_crm
import admin_panel
import email_utils
import time

# --- Configuração Global ---
st.set_page_config(page_title="Gestão Correspondente", layout="wide", page_icon="🏦")
db.init_db()

# --- CSS PERSONALIZADO (ESTILO DA IMAGEM ROXA) ---
st.markdown("""
    <style>
    /* 1. Fundo Gradiente Roxo (Igual à imagem) */
    .stApp {
        background: linear-gradient(135deg, #8E2DE2 0%, #4A00E0 100%);
        background-attachment: fixed;
    }

    /* 2. Esconder menus padrões do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 3. Estilo do Cartão Branco (Centralizado) */
    /* Isso afeta a coluna do meio quando estamos na tela de login */
    div[data-testid="column"]:nth-of-type(2) {
        background-color: white;
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    }

    /* 4. Títulos e Textos dentro do cartão */
    h1 {
        color: #333 !important;
        font-family: sans-serif;
        font-weight: 800;
        font-size: 26px !important;
        text-align: center;
        padding-bottom: 0px;
    }
    
    p {
        color: #666;
        text-align: center;
        font-size: 14px;
    }

    /* 5. Inputs (Caixas de Texto) */
    .stTextInput>div>div>input {
        background-color: #f0f2f5;
        border: none;
        border-radius: 10px;
        color: #333;
        padding: 12px;
    }
    
    /* Remover borda de foco azul padrão e por uma roxa suave */
    .stTextInput>div>div>input:focus {
        box-shadow: 0 0 0 2px #8E2DE2;
    }

    /* 6. Botões (Degradê Roxo) */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #8E2DE2 0%, #4A00E0 100%);
        color: white;
        border: none;
        border-radius: 25px; /* Bem arredondado igual a imagem */
        padding: 12px;
        font-weight: bold;
        font-size: 16px;
        margin-top: 10px;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        color: white;
        box-shadow: 0 5px 15px rgba(74, 0, 224, 0.4);
    }

    /* 7. Abas (Tabs) Limpas */
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
        gap: 20px;
        border-bottom: 1px solid #eee;
        padding-bottom: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border: none;
        color: #999;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        color: #4A00E0 !important;
        border-bottom: 2px solid #4A00E0;
    }
    
    /* Ajuste para mensagens de erro/sucesso ficarem legíveis no fundo branco */
    .stAlert {
        background-color: #f8f9fa;
        border: 1px solid #ddd;
    }
    </style>
""", unsafe_allow_html=True)

# --- Controle de Sessão ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'role' not in st.session_state: st.session_state.role = ''
if 'username' not in st.session_state: st.session_state.username = ''
if 'recup_etapa' not in st.session_state: st.session_state.recup_etapa = 0

# ==========================================
# TELA DE LOGIN (LAYOUT DA IMAGEM)
# ==========================================
if not st.session_state.logged_in:
    
    # Colunas: [Espaço Vazio] [Cartão Branco] [Espaço Vazio]
    # Ajustei as proporções para o cartão não ficar nem muito largo nem muito estreito
    c1, c2, c3 = st.columns([1, 1.2, 1])
    
    with c2:
        # Ícone do Sistema (Pode ser uma imagem ou emoji grande)
        st.markdown("<div style='text-align: center; font-size: 60px; margin-bottom: -20px;'>🏦</div>", unsafe_allow_html=True)
        
        st.title("Gestão Correspondente")
        st.write("Sistema CRM para Correspondentes Bancários")
        
        st.write("") # Espaço
        
        # Abas de navegação
        tab_entrar, tab_criar = st.tabs(["Entrar", "Registar"])
        
        # --- ABA ENTRAR ---
        with tab_entrar:
            st.write("")
            u = st.text_input("Utilizador", placeholder="Digite seu usuário", key="login_u")
            p = st.text_input("Senha", type="password", placeholder="••••••••", key="login_p")
            
            # Link de esqueceu senha (simulado)
            with st.expander("Esqueceu a senha?", expanded=False):
                if st.session_state.recup_etapa == 0:
                    ru = st.text_input("Usuário", key="ru")
                    re = st.text_input("E-mail", key="re")
                    if st.button("Enviar Código", key="btn_env_cod"):
                        res = db.iniciar_recuperacao_senha(ru, re)
                        if res['status']:
                            email_utils.email_recuperacao(re, res['codigo'])
                            st.session_state.recup_etapa = 1
                            st.session_state.rec_user_temp = ru
                            st.success("Enviado!")
                            time.sleep(1); st.rerun()
                        else: st.error(res['msg'])
                elif st.session_state.recup_etapa == 1:
                    st.info(f"Código para: {st.session_state.rec_user_temp}")
                    rc = st.text_input("Código")
                    rn = st.text_input("Nova Senha", type="password")
                    if st.button("Confirmar", key="btn_conf_sen"):
                        if db.finalizar_recuperacao_senha(st.session_state.rec_user_temp, rc, rn):
                            st.success("Alterada!"); st.session_state.recup_etapa = 0; time.sleep(1); st.rerun()
                        else: st.error("Erro.")

            st.write("")
            if st.button("Entrar ➔"):
                r = db.verificar_login(u, p)
                if r['status'] == 'success':
                    if r['approved']:
                        st.session_state.logged_in = True
                        st.session_state.role = r['role']
                        st.session_state.username = u
                        st.rerun()
                    else: st.warning("Aguarde aprovação.")
                else: st.error(r['msg'])

        # --- ABA CRIAR CONTA ---
        with tab_criar:
            st.write("")
            nu = st.text_input("Criar Usuário", placeholder="Ex: joaosilva", key="reg_u")
            ne = st.text_input("E-mail", placeholder="email@exemplo.com", key="reg_e")
            np = st.text_input("Senha", type="password", placeholder="••••••••", key="reg_p")
            npc = st.text_input("Confirmar", type="password", placeholder="••••••••", key="reg_pc")
            
            st.write("")
            if st.button("Criar Conta"):
                if np != npc: st.error("Senhas não batem.")
                else:
                    res = db.registrar_usuario(nu, np, ne)
                    if res['status']:
                        st.success(f"Criado! ID: {res['id_gerado']}")
                        email_utils.email_boas_vindas(nu, ne)
                    else: st.error(res['msg'])
        
        st.markdown("<br><div style='text-align: center; color: #999; font-size: 11px;'>EDWCRED © 2026</div>", unsafe_allow_html=True)

# ==========================================
# SISTEMA INTERNO (LAYOUT LIMPO)
# ==========================================
else:
    # Remove o fundo roxo e o estilo de cartão quando entra no sistema
    st.markdown("""
        <style>
        .stApp {
            background: #ffffff; /* Fundo branco limpo */
        }
        div[data-testid="column"]:nth-of-type(2) {
            background-color: transparent;
            box-shadow: none;
            padding: 0;
        }
        .stButton>button {
            background: #00b894; /* Botão verde padrão do sistema */
            border-radius: 5px;
        }
        h1 { text-align: left; }
        p { text-align: left; }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.write(f"👤 **{st.session_state.username}**")
        pg = "CRM"
        if st.session_state.role == 'admin':
            pg = st.radio("Menu", ["CRM", "Admin Panel"])
            
        st.markdown("---")
        if st.button("Sair", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
            
    if pg == "CRM": 
        app_crm.render_crm()
    elif pg == "Admin Panel": 
        admin_panel.render_admin()