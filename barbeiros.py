import streamlit as st
import uuid

def barbeiros_page(db):
    st.title("Barbeiros")

    barbearia_id = st.session_state["user"]
    barbeiros_ref = db.collection("barbearias").document(barbearia_id).collection("barbeiros")

    with st.expander("➕ Cadastrar novo barbeiro"):
        nome = st.text_input("Nome do barbeiro")
        email = st.text_input("Email")
        telefone = st.text_input("Telefone")

        if st.button("Cadastrar barbeiro"):
            if nome and email:
                barbeiro_id = str(uuid.uuid4())
                barbeiros_ref.document(barbeiro_id).set({
                    "id": barbeiro_id,
                    "nome": nome,
                    "email": email,
                    "telefone": telefone
                })
                st.success("Barbeiro cadastrado com sucesso!")
                st.rerun()
            else:
                st.warning("Preencha nome e email.")

    st.subheader("📋 Lista de barbeiros")
    barbeiros = barbeiros_ref.stream()

    for barbeiro in barbeiros:
        dados = barbeiro.to_dict()
        with st.container():
            st.markdown(f"""
            **Nome:** {dados['nome']}  
            **Email:** {dados['email']}  
            **Telefone:** {dados['telefone']}
            """)
            st.markdown("---")
