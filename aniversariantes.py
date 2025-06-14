import streamlit as st
from datetime import datetime
from email_utils import enviar_email_promocional

def aniversariantes_page(db):
    st.title("🎉 Aniversariantes do dia")

    barbearia_id = st.session_state["user"]
    clientes_ref = db.collection("barbearias").document(barbearia_id).collection("clientes")

    hoje = datetime.now().strftime("%m-%d")
    aniversariantes = []

    for doc in clientes_ref.stream():
        cliente = doc.to_dict()
        nascimento = cliente.get("nascimento")  # formato YYYY-MM-DD
        if nascimento and nascimento[5:] == hoje:
            aniversariantes.append(cliente)

    if aniversariantes:
        st.success(f"🎂 Encontrado(s) {len(aniversariantes)} aniversariante(s) hoje!")
        for c in aniversariantes:
            st.markdown(f"""
            **Nome:** {c['nome']}  
            **Email:** {c['email']}  
            **Telefone:** {c['telefone']}
            """)
            st.markdown("---")

        if st.button("📩 Enviar e-mails promocionais"):
            for cliente in aniversariantes:
                enviar_email_promocional(cliente["email"], cliente["nome"])
            st.success("E-mails enviados com sucesso!")

    else:
        st.info("Nenhum aniversariante hoje.")
