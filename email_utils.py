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
    assunto = "Registro Recebido - EDWCRED"
    corpo = f"""
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; padding: 30px; border-radius: 12px; background-color: #ffffff;">
        <h2 style="color: #7c3aed; margin-top: 0;">Olá, {nome}!</h2>
        
        <p style="font-size: 16px; line-height: 1.5;">Recebemos o seu registro com sucesso em nosso sistema.</p>
        
        <p style="font-size: 16px; line-height: 1.5;">No momento, seu cadastro está em análise e aguardando a aprovação do administrador.<br>
        Assim que a aprovação for concluída, você receberá uma nova notificação com seus dados de acesso.</p>
        
        <div style="background-color: #f8fafc; padding: 15px; border-left: 4px solid #7c3aed; margin: 20px 0; border-radius: 4px;">
            <p style="margin: 0; color: #475569;"><strong>⏳ Prazo:</strong> a liberação costuma ocorrer em breve, conforme a validação das informações cadastradas.</p>
        </div>
        
        <p style="font-size: 14px; color: #64748b;">📩 Caso tenha dúvidas ou precise de suporte, entre em contato com o administrador do sistema.</p>
        
        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 30px 0;">
        
        <p style="color: #94a3b8; font-size: 12px; text-align: center; margin: 0;">EDWCRED • Sistema Automático</p>
    </div>
    """
    return enviar_email(email_destino, assunto, corpo)

def email_aprovado(nome, email_destino, usuario, senha, user_id="N/A"):
    assunto = "✅ Acesso Aprovado - EDWCRED"
    link_sistema = "https://sistema-7usqqp4kwbvltogwpmroj4.streamlit.app/"
    
    corpo = f"""
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; padding: 30px; border-radius: 12px; background-color: #ffffff;">
        <h2 style="color: #7c3aed; margin-top: 0;">Parabéns, {nome}!</h2>
        <p style="font-size: 16px;">Seu acesso ao sistema foi aprovado com sucesso.</p>

        <h3 style="color: #1e293b; border-bottom: 1px solid #e2e8f0; padding-bottom: 10px; margin-top: 25px;">🔐 Dados de acesso</h3>
        
        <div style="background-color: #f1f5f9; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
            <p style="margin: 8px 0; font-size: 15px;"><strong>ID do Utilizador:</strong> #{user_id}</p>
            <p style="margin: 8px 0; font-size: 15px;"><strong>Login:</strong> {usuario}</p>
            <p style="margin: 8px 0; font-size: 15px;"><strong>Senha:</strong> {senha}</p>
        </div>

        <h3 style="color: #1e293b;">🌐 Acesso ao sistema</h3>
        
        <div style="text-align: center; margin: 25px 0;">
            <a href="{link_sistema}" style="background-color: #7c3aed; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">👉 Acessar Sistema Agora</a>
        </div>
        <p style="font-size: 12px; color: #64748b; text-align: center;">Ou acesse: {link_sistema}</p>

        <div style="background-color: #fff7ed; padding: 15px; border-radius: 6px; border: 1px solid #ffedd5; margin-top: 25px; color: #9a3412; font-size: 14px;">
            🔒 <strong>Recomendamos que altere sua senha no primeiro acesso, garantindo maior segurança da sua conta.</strong>
        </div>

        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 30px 0;">

        <h4 style="margin-bottom: 10px; color: #1e293b;">📩 Suporte e atendimento</h4>
        <p style="font-size: 14px; color: #64748b; margin-top: 0; line-height: 1.5;">
            Em caso de dúvidas, erros ou identificação de bugs, entre em contato com o Administrador ou envie um e-mail para:<br>
            <a href="mailto:contato@edwcred.com.br" style="color: #7c3aed; text-decoration: none; font-weight: 500;">contato@edwcred.com.br</a>
        </p>
    </div>
    """
    return enviar_email(email_destino, assunto, corpo)

def email_recuperacao(email_destino, codigo):
    assunto = "🔑 Recuperar Senha - EDWCRED"
    corpo = f"""
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; max-width: 500px; margin: 0 auto; border: 1px solid #e2e8f0; padding: 30px; border-radius: 12px; text-align: center;">
        <h2 style="color: #0f172a;">Código de Recuperação</h2>
        <p style="color: #64748b;">Use este código para redefinir sua senha:</p>
        
        <div style="background: #f1f5f9; padding: 20px; border-radius: 8px; margin: 25px 0;">
            <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #7c3aed;">{codigo}</span>
        </div>
        
        <p style="font-size: 12px; color: #94a3b8;">Se você não solicitou isso, ignore este e-mail.</p>
    </div>
    """
    return enviar_email(email_destino, assunto, corpo)

def email_acesso_removido(nome, email_destino):
    assunto = "⛔ Acesso Removido - EDWCRED"
    corpo = f"""
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; padding: 30px; border-radius: 12px; background-color: #ffffff;">
        <h2 style="color: #dc2626; margin-top: 0;">Olá, {nome}!</h2>
        
        <p style="font-size: 16px; line-height: 1.5; margin-top: 20px;">Informamos que seu acesso ao sistema foi removido.</p>
        
        <div style="background-color: #fef2f2; padding: 15px; border-left: 4px solid #dc2626; margin: 20px 0; border-radius: 4px;">
            <p style="margin: 0; color: #991b1b; line-height: 1.5;">A partir deste momento, não será mais possível realizar login ou utilizar as funcionalidades da plataforma com este usuário.</p>
        </div>
        
        <p style="font-size: 14px; color: #64748b; line-height: 1.5;">📩 Caso considere que isso seja um engano ou precise de mais informações, entre em contato com o administrador do sistema para esclarecimentos.</p>
        
        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 30px 0;">
        
        <p style="color: #94a3b8; font-size: 12px; text-align: center; margin: 0;">EDWCRED • Sistema Automático</p>
    </div>
    """
    return enviar_email(email_destino, assunto, corpo)
