import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
import time
from functools import wraps

# --- CONFIGURAÇÃO ---
SPREADSHEET_ID = "1BsHA6adHib36GWijD_rwTg5btj94KegFoKf-ztKqTik"

COLUNAS_CLIENTES = [
    "id", "nome", "telefone", "cpf", "tipo", "sub_categoria", "status_venda",
    "data_nascimento", "ultimo_contato", "notas", "criado_em",
    "cep", "endereco", "numero", "bairro", "cidade", "estado", "nome_mae",
    "pix_chave", "dados_bancarios", "usuario_responsavel", "data_termino", "data_consulta"
]

COLUNAS_USUARIOS = [
    "username", "password", "role", "approved", "email", "user_id", "recovery_code"
]

# --- DECORATOR PARA TENTATIVA AUTOMÁTICA (ANTI-429) ---
def retry_api(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        max_retries = 5
        for i in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                erro_str = str(e)
                # Se for erro de cota (429) ou erro de conexão
                if "429" in erro_str or "Quota" in erro_str or "APIError" in erro_str:
                    wait_time = (2 ** i) + random.uniform(0, 1) # 2s, 4s, 8s, 16s...
                    time.sleep(wait_time)
                    continue
                else:
                    raise e
        # Se falhar todas as tentativas
        st.error("⚠️ O Google Sheets está ocupado. Aguarde alguns segundos e recarregue a página.")
        st.stop()
    return wrapper

# --- CONEXÃO ---
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
        st.error(f"Erro de autenticação: {e}")
        st.stop()

@retry_api
def get_worksheet(name):
    client = get_connection()
    try:
        sh = client.open_by_key(SPREADSHEET_ID)
    except Exception as e:
        raise e # Deixa o retry lidar com isso
        
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

# --- CACHE (5 MINUTOS) ---
@st.cache_data(ttl=300) 
@retry_api
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
        
        for col in COLUNAS_CLIENTES:
            if col not in df.columns: df[col] = ""

        if 'id' in df.columns:
            df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(0).astype(int)

        if filtro_usuario and filtro_usuario != "Todos":
            df = df[df['usuario_responsavel'] == filtro_usuario]
        return df
    except Exception as e:
        return pd.DataFrame(columns=COLUNAS_CLIENTES)

@retry_api
def add_cliente(dados):
    ws = get_worksheet("clientes")
    # Tenta pegar ID sem ler a planilha toda se possível, ou usa cache se arriscado
    # Aqui vamos ler direto, mas protegido pelo retry
    all_data = ws.col_values(1) # Lê apenas a primeira coluna (mais leve)
    
    new_id = 1
    if len(all_data) > 1: # Tem cabeçalho e dados
        try:
            ids = [int(x) for x in all_data[1:] if x.isdigit()]
            if ids: new_id = max(ids) + 1
        except: pass
    
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

@retry_api
def update_cliente_completo(id_cliente, dados):
    ws = get_worksheet("clientes")
    cell = ws.find(str(id_cliente), in_column=1)
    r = cell.row
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

@retry_api
def delete_cliente(cliente_id):
    ws = get_worksheet("clientes")
    cell = ws.find(str(cliente_id), in_column=1)
    ws.delete_rows(cell.row)
    limpar_cache()

# --- USUÁRIOS ---
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
        return {"status": "fail", "msg": str(e)}

@retry_api
def registrar_usuario(username, password, email, role='user', approved=0):
    ws = get_worksheet("usuarios")
    # Validação rápida lendo a coluna 1 e 5
    users = ws.col_values(1)
    emails = ws.col_values(5)
    
    if username in users: return {"status": False, "msg": "Usuário já existe"}
    if email in emails: return {"status": False, "msg": "E-mail já cadastrado"}
    
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

@retry_api
def aprovar_usuario(username):
    ws = get_worksheet("usuarios")
    cell = ws.find(username, in_column=1)
    ws.update_cell(cell.row, 4, 1)
    limpar_cache()

@retry_api
def deletar_usuario(username):
    ws = get_worksheet("usuarios")
    cell = ws.find(username, in_column=1)
    ws.delete_rows(cell.row)
    limpar_cache()

@retry_api
def update_usuario(old_username, new_data):
    ws = get_worksheet("usuarios")
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

@retry_api
def iniciar_recuperacao_senha(username, email):
    ws = get_worksheet("usuarios")
    cell = ws.find(username, in_column=1)
    row_data = ws.row_values(cell.row)
    if len(row_data) >= 5 and row_data[4] == email:
        codigo = str(random.randint(100000, 999999))
        ws.update_cell(cell.row, 7, codigo)
        return {"status": True, "codigo": codigo}
    return {"status": False, "msg": "Dados incorretos"}

@retry_api
def finalizar_recuperacao_senha(username, codigo, nova_senha):
    ws = get_worksheet("usuarios")
    cell = ws.find(username, in_column=1)
    code_on_db = ws.cell(cell.row, 7).value
    if str(code_on_db) == str(codigo):
        ws.update_cell(cell.row, 2, nova_senha)
        ws.update_cell(cell.row, 7, "")
        limpar_cache()
        return True
    return False
