import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

# ==========================================================
# CONFIGURAÇÃO DO E-MAIL (PREENCHA AQUI)
# ==========================================================
SMTP_SERVER = "smtp.hostinger.com"
SMTP_PORT = 587
# O e-mail pode ficar aqui, não é segredo
REMETENTE_EMAIL = "contato@edwcred.com.br"

def get_senha_email():
    # Tenta pegar dos segredos do Streamlit
    try:
        return st.secrets["email_senha"]
    except:
        return None

def enviar_email(destinatario, assunto, mensagem_html):
    senha = get_senha_email()
    
    if not senha:
        print("⚠️ Senha de e-mail não encontrada nos Secrets.")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = REMETENTE_EMAIL
        msg['To'] = destinatario
        msg['Subject'] = assunto
        msg.attach(MIMEText(mensagem_html, 'html'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(REMETENTE_EMAIL, senha)
        text = msg.as_string()
        server.sendmail(REMETENTE_EMAIL, destinatario, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Erro e-mail: {e}")
        return False

def email_boas_vindas(nome, email_destino):
    assunto = "Registro Recebido - EDWCRED"
    corpo = f"""
    <div style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <h2 style="color: #00b894;">Olá, {nome}!</h2>
        <p>Recebemos o seu registro no sistema <b>Gestão Correspondente da EDWCRED</b>.</p>
        <p>Seu acesso está aguardando aprovação do administrador.</p>
        <hr>
        <p style="font-size: 12px; color: #999;">EDWCRED - Sistema Automático</p>
    </div>
    """
    return enviar_email(email_destino, assunto, corpo)

def email_aprovado(nome, email_destino, usuario, senha, user_id="N/A"):
    assunto = "✅ Acesso Liberado - EDWCRED"
    corpo = f"""
    <div style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <h2 style="color: #00b894;">Parabéns, {nome}!</h2>
        <p>Seu acesso ao sistema <b>Gestão Correspondente da EDWCRED</b> foi aprovado.</p>
        <div style="background-color: #f1f2f6; padding: 15px; border-radius: 5px; border-left: 5px solid #00b894;">
            <p style="margin: 5px 0;"><b>ID Usuário:</b> #{user_id}</p>
            <p style="margin: 5px 0;"><b>Login:</b> {usuario}</p>
            <p style="margin: 5px 0;"><b>Senha:</b> {senha}</p>
        </div>
        <p>Acesse o sistema para começar a operar.</p>
        <hr>
        <p style="font-size: 12px; color: #999;">Mantenha seus dados seguros.</p>
    </div>
    """
    return enviar_email(email_destino, assunto, corpo)

def email_recuperacao(email_destino, codigo):
    assunto = "🔑 Recuperação de Senha - EDWCRED"
    corpo = f"""
    <div style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #d63031;">Recuperação de Senha</h2>
        <p>Recebemos um pedido para redefinir sua senha.</p>
        <p>Use o código abaixo no sistema:</p>
        <div style="font-size: 24px; font-weight: bold; color: #333; background: #eee; padding: 10px; text-align: center; width: 150px;">
            {codigo}
        </div>
        <p>Se não foi você, ignore este e-mail.</p>
    </div>
    """
    return enviar_email(email_destino, assunto, corpo)