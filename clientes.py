import streamlit as st
from datetime import date
import uuid

def clientes_page(db):
    st.title("Clientes")

    barbearia_id = st.session_state["user"]  # Cada barbearia tem seu próprio ID de usuário
    clientes_ref = db.collection("barbearias").document(barbearia_id).collection("clientes")

    with st.expander("➕ Cadastrar novo cliente"):
        nome = st.text_input("Nome completo")
        email = st.text_input("Email")
        telefone = st.text_input("Telefone")
        nascimento = st.date_input("Data de nascimento", value=date(2000, 1, 1), format="DD/MM/YYYY")
       # qtd_cortes = st.number_input("Quantidade de cortes já realizados", min_value=0, step=1)

        if st.button("Cadastrar cliente"):
            if nome and email:
                cliente_id = str(uuid.uuid4())
                clientes_ref.document(cliente_id).set({
                    "id": cliente_id,
                    "nome": nome,
                    "email": email,
                    "telefone": telefone,
                    "nascimento": nascimento.strftime("%Y-%m-%d")
             #       "qtd_cortes": qtd_cortes
                })
                st.success("Cliente cadastrado com sucesso!")
                st.rerun()
            else:
                st.warning("Preencha nome e email.")

    st.subheader("📋 Lista de clientes")
    clientes = clientes_ref.stream()

    for cliente in clientes:
        dados = cliente.to_dict()
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            st.markdown(f"""
            **Nome:** {dados['nome']}  
            **Email:** {dados['email']}  
            **Telefone:** {dados['telefone']}  
            **Nascimento:** {dados['nascimento']}  
            **Qtd. de cortes:** {dados['qtd_cortes']}
            """)
        with col2:
            if st.button("❌", key=f"del_{dados['id']}"):
                clientes_ref.document(dados["id"]).delete()
                st.success(f"Cliente '{dados['nome']}' deletado com sucesso!")
                st.rerun()

        st.markdown("---")
