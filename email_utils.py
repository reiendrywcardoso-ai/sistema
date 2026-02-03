import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

# --- CONFIGURAÇÃO ---
SMTP_SERVER = "smtp.hostinger.com"
SMTP_PORT = 587
REMETENTE_EMAIL = "contato@edwcred.com.br"

def get_senha_email():
    try: return st.secrets["email_senha"]
    except: return None

def enviar_email(destinatario, assunto, mensagem_html):
    senha = get_senha_email()
    if not senha: return False

    try:
        msg = MIMEMultipart()
        msg['From'] = REMETENTE_EMAIL
        msg['To'] = destinatario
        msg['Subject'] = assunto
        msg.attach(MIMEText(mensagem_html, 'html'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(REMETENTE_EMAIL, senha)
        server.sendmail(REMETENTE_EMAIL, destinatario, msg.as_string())
        server.quit()
        return True
    except: return False

def email_boas_vindas(nome, email_destino):
    assunto = "Registo Recebido - EDWCRED"
    corpo = f"""
    <div style="font-family: Arial; color: #333;">
        <h2 style="color: #00b894;">Olá, {nome}!</h2>
        <p>Recebemos o seu registo.</p>
        <p>Aguarde a aprovação do administrador.</p>
        <hr>
        <small>EDWCRED Automático</small>
    </div>
    """
    return enviar_email(email_destino, assunto, corpo)

def email_aprovado(nome, email_destino, usuario, senha, user_id="N/A"):
    assunto = "✅ Acesso Aprovado - EDWCRED"
    corpo = f"""
    <div style="font-family: Arial; color: #333;">
        <h2 style="color: #00b894;">Parabéns, {nome}!</h2>
        <p>Acesso aprovado.</p>
        <div style="background: #f1f2f6; padding: 15px; border-radius: 5px;">
            <p><b>ID de Utilizador:</b> #{user_id}</p>
            <p><b>Login:</b> {usuario}</p>
            <p><b>Senha:</b> {senha}</p>
        </div>
        <p>Acesse o sistema agora.</p>
    </div>
    """
    return enviar_email(email_destino, assunto, corpo)

def email_recuperacao(email_destino, codigo):
    assunto = "🔑 Recuperar Senha - EDWCRED"
    corpo = f"""
    <div style="font-family: Arial; color: #333;">
        <h2>Código de Recuperação</h2>
        <p>Use este código para mudar a senha:</p>
        <h1 style="background: #eee; padding: 10px; display: inline-block;">{codigo}</h1>
    </div>
    """
    return enviar_email(email_destino, assunto, corpo)