import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random

# --- CONFIGURAÇÃO ---
SPREADSHEET_ID = "1BsHA6adHib36GWijD_rwTg5btj94KegFoKf-ztKqTik"

# Adicionei 'data_termino' e 'data_consulta'
COLUNAS_CLIENTES = [
    "id", "nome", "telefone", "cpf", "tipo", "sub_categoria", "status_venda",
    "data_nascimento", "ultimo_contato", "notas", "criado_em",
    "cep", "endereco", "numero", "bairro", "cidade", "estado", "nome_mae",
    "pix_chave", "dados_bancarios", "usuario_responsavel", "data_termino", "data_consulta"
]

COLUNAS_USUARIOS = [
    "username", "password", "role", "approved", "email", "user_id", "recovery_code"
]

# --- CONEXÃO COM GOOGLE SHEETS ---
def get_connection():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            return client
        else:
            st.error("❌ ERRO: Chave do Google não encontrada nos Secrets.")
            st.stop()
    except Exception as e:
        st.error(f"Erro de autenticação nos segredos: {e}")
        st.stop()

def get_worksheet(name):
    client = get_connection()
    sh = None
    try:
        sh = client.open_by_key(SPREADSHEET_ID)
    except Exception as e:
        st.error("❌ ERRO: O robô não conseguiu entrar na planilha.")
        st.stop()
        
    try:
        ws = sh.worksheet(name)
        return ws
    except:
        try:
            ws = sh.add_worksheet(title=name, rows=1000, cols=30)
            if name == "clientes": ws.append_row(COLUNAS_CLIENTES)
            elif name == "usuarios": 
                ws.append_row(COLUNAS_USUARIOS)
                ws.append_row(["admin", "1234", "admin", 1, "admin@sistema.com", 1000, ""])
            return ws
        except Exception as e:
            st.error(f"Erro ao criar aba '{name}': {e}")
            st.stop()

def init_db():
    get_worksheet("clientes")
    get_worksheet("usuarios")

# --- FUNÇÕES DE CACHE ---
@st.cache_data(ttl=60)
def _fetch_all_data(sheet_name):
    ws = get_worksheet(sheet_name)
    return ws.get_all_records()

def limpar_cache():
    st.cache_data.clear()

# --- CLIENTES ---
def get_clientes(filtro_usuario=None):
    try:
        data = _fetch_all_data("clientes")
        df = pd.DataFrame(data)
        
        if df.empty: return pd.DataFrame(columns=COLUNAS_CLIENTES)
        
        # Garante colunas novas
        for col in COLUNAS_CLIENTES:
            if col not in df.columns: df[col] = ""

        if 'id' in df.columns:
            df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(0).astype(int)

        if filtro_usuario and filtro_usuario != "Todos":
            df = df[df['usuario_responsavel'] == filtro_usuario]
        return df
    except Exception as e:
        return pd.DataFrame(columns=COLUNAS_CLIENTES)

def add_cliente(dados):
    ws = get_worksheet("clientes")
    data = _fetch_all_data("clientes")
    
    if not data: new_id = 1
    else: 
        ids = [int(row['id']) for row in data if str(row['id']).isdigit()]
        new_id = max(ids) + 1 if ids else 1
    
    nova_linha = [
        new_id,
        dados.get('nome', ''), dados.get('telefone', ''), dados.get('cpf', ''),
        dados.get('tipo', ''), dados.get('sub_categoria', ''), dados.get('status_venda', ''),
        str(dados.get('data_nascimento', '')), str(datetime.now().date()), dados.get('notas', ''), str(datetime.now().date()),
        dados.get('cep', ''), dados.get('endereco', ''), dados.get('numero', ''),
        dados.get('bairro', ''), dados.get('cidade', ''), dados.get('estado', ''),
        dados.get('nome_mae', ''), dados.get('pix_chave', ''), dados.get('dados_bancarios', ''),
        dados.get('usuario_responsavel', 'admin'),
        str(dados.get('data_termino', '')), str(dados.get('data_consulta', ''))
    ]
    ws.append_row(nova_linha)
    limpar_cache()

def update_cliente_completo(id_cliente, dados):
    ws = get_worksheet("clientes")
    try:
        cell = ws.find(str(id_cliente), in_column=1)
        r = cell.row
        
        # Mapeamento de colunas (Index começa em 1)
        # 22: data_termino, 23: data_consulta
        updates = [
            (r, 2, dados.get('nome')), (r, 3, dados.get('telefone')), (r, 4, dados.get('cpf')),
            (r, 5, dados.get('tipo')), (r, 6, dados.get('sub_categoria')), (r, 7, dados.get('status_venda')),
            (r, 8, str(dados.get('data_nascimento'))), (r, 10, dados.get('notas')),
            (r, 12, dados.get('cep')), (r, 13, dados.get('endereco')), (r, 14, dados.get('numero')),
            (r, 15, dados.get('bairro')), (r, 16, dados.get('cidade')), (r, 17, dados.get('estado')),
            (r, 18, dados.get('nome_mae')), (r, 19, dados.get('pix_chave')), (r, 20, dados.get('dados_bancarios')),
            (r, 22, str(dados.get('data_termino', ''))), (r, 23, str(dados.get('data_consulta', '')))
        ]
        batch = []
        for row, col, val in updates:
            if val is not None:
                batch.append({'range': gspread.utils.rowcol_to_a1(row, col), 'values': [[val]]})
        ws.batch_update(batch)
        limpar_cache()
    except: pass

def delete_cliente(cliente_id):
    ws = get_worksheet("clientes")
    try:
        cell = ws.find(str(cliente_id), in_column=1)
        ws.delete_rows(cell.row)
        limpar_cache()
    except: pass

# --- USUÁRIOS (Sem Alteração) ---
def verificar_login(username, password):
    try:
        data = _fetch_all_data("usuarios")
        for row in data:
            if str(row['username']) == username:
                if str(row['password']) == password:
                    return {"status": "success", "role": row['role'], "approved": str(row['approved']) == "1"}
                return {"status": "fail", "msg": "Senha incorreta"}
        return {"status": "fail", "msg": "Usuário não encontrado"}
    except Exception as e:
        return {"status": "fail", "msg": f"Erro: {str(e)}"}

def registrar_usuario(username, password, email, role='user', approved=0):
    data = _fetch_all_data("usuarios")
    for row in data:
        if str(row['username']) == username: return {"status": False, "msg": "Usuário já existe"}
        if str(row['email']) == email: return {"status": False, "msg": "E-mail já cadastrado"}
    
    ws = get_worksheet("usuarios")       
    new_id = random.randint(100000, 999999)
    ws.append_row([username, password, role, approved, email, new_id, ""])
    limpar_cache()
    return {"status": True, "msg": "Sucesso", "id_gerado": new_id}

def get_usuarios_pendentes():
    df = get_todos_usuarios()
    if df.empty: return df
    return df[df['approved'].astype(str) == "0"]

def get_todos_usuarios():
    data = _fetch_all_data("usuarios")
    return pd.DataFrame(data)

def get_lista_nomes_usuarios():
    df = get_todos_usuarios()
    if df.empty: return []
    return df['username'].tolist()

def aprovar_usuario(username):
    ws = get_worksheet("usuarios")
    try:
        cell = ws.find(username, in_column=1)
        ws.update_cell(cell.row, 4, 1)
        limpar_cache()
    except: pass

def deletar_usuario(username):
    ws = get_worksheet("usuarios")
    try:
        cell = ws.find(username, in_column=1)
        ws.delete_rows(cell.row)
        limpar_cache()
    except: pass

def update_usuario(old_username, new_data):
    ws = get_worksheet("usuarios")
    try:
        cell = ws.find(str(old_username), in_column=1)
        r = cell.row
        updates = [
            {'range': gspread.utils.rowcol_to_a1(r, 1), 'values': [[new_data['username']]]},
            {'range': gspread.utils.rowcol_to_a1(r, 2), 'values': [[new_data['password']]]},
            {'range': gspread.utils.rowcol_to_a1(r, 3), 'values': [[new_data['role']]]},
            {'range': gspread.utils.rowcol_to_a1(r, 5), 'values': [[new_data['email']]]}
        ]
        ws.batch_update(updates)
        limpar_cache()
        return True
    except: return False

def iniciar_recuperacao_senha(username, email):
    ws = get_worksheet("usuarios")
    try:
        cell = ws.find(username, in_column=1)
        row_data = ws.row_values(cell.row)
        if len(row_data) >= 5 and row_data[4] == email:
            codigo = str(random.randint(100000, 999999))
            ws.update_cell(cell.row, 7, codigo)
            return {"status": True, "codigo": codigo}
    except: pass
    return {"status": False, "msg": "Dados incorretos"}

def finalizar_recuperacao_senha(username, codigo, nova_senha):
    ws = get_worksheet("usuarios")
    try:
        cell = ws.find(username, in_column=1)
        code_on_db = ws.cell(cell.row, 7).value
        if str(code_on_db) == str(codigo):
            ws.update_cell(cell.row, 2, nova_senha)
            ws.update_cell(cell.row, 7, "")
            limpar_cache()
            return True
    except: pass
    return False
