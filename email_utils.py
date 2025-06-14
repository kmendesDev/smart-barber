import smtplib
from email.mime.text import MIMEText
import streamlit as st

def enviar_email_promocional(destinatario, nome_cliente):
    remetente = st.secrets["EMAIL"]["remetente"]
    senha = st.secrets["EMAIL"]["senha"]

    assunto = "🎉 Feliz Aniversário! Ganhe 20% de desconto 🎁"
    corpo = f"""
    Olá {nome_cliente}!

    Em comemoração ao seu aniversário, preparamos uma surpresa especial:
    🎁 Você ganhou 20% de desconto em qualquer serviço da nossa barbearia!

    Aproveite seu dia com estilo. Esperamos você!

    Um grande abraço da equipe!
    """

    msg = MIMEText(corpo)
    msg["Subject"] = assunto
    msg["From"] = remetente
    msg["To"] = destinatario

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
            servidor.login(remetente, senha)
            servidor.sendmail(remetente, destinatario, msg.as_string())
    except Exception as e:
        print(f"Erro ao enviar para {destinatario}: {e}")
