import streamlit as st
from datetime import datetime
import uuid

def realizar_servico_page(db):
    st.title("Registrar Serviço Realizado")

    barbearia_id = st.session_state["user"]  # pegar o id da barbearia do usuário logado

    # Buscar clientes da barbearia
    clientes_ref = db.collection("barbearias").document(barbearia_id).collection("clientes").stream()
    clientes = {doc.id: doc.to_dict() for doc in clientes_ref}
    if not clientes:
        st.warning("Nenhum cliente cadastrado.")
        return

    # Buscar barbeiros da barbearia
    barbeiros_ref = db.collection("barbearias").document(barbearia_id).collection("barbeiros").stream()
    barbeiros = {doc.id: doc.to_dict() for doc in barbeiros_ref}
    if not barbeiros:
        st.warning("Nenhum barbeiro cadastrado.")
        return

    # Selectboxes para cliente e barbeiro, formatando para mostrar o nome
    cliente_selecionado = st.selectbox("Cliente", list(clientes.values()), format_func=lambda c: c["nome"])
    barbeiro_selecionado = st.selectbox("Barbeiro", list(barbeiros.values()), format_func=lambda b: b["nome"])

    servico = st.selectbox("Serviço", [
        "Corte de Cabelo", "Barba", "Pezinho", "Coloração",
        "Corte + Barba", "Coloração + Corte", "Coloração + Barba"
    ])
    valor = st.number_input("Valor cobrado (R$)", min_value=0.0, format="%.2f")
    data_atendimento = st.date_input("Data do atendimento", value=datetime.today())

    if st.button("Registrar Serviço"):
        servico_id = str(uuid.uuid4())
        # Registrar serviço dentro da barbearia
        db.collection("barbearias").document(barbearia_id).collection("servicos").document(servico_id).set({
            "id": servico_id,
            "cliente_id": cliente_selecionado["id"],
            "cliente_nome": cliente_selecionado["nome"],
            "barbeiro_id": barbeiro_selecionado["id"],
            "barbeiro_nome": barbeiro_selecionado["nome"],
            "servico": servico,
            "valor": valor,
            "data": data_atendimento.strftime("%Y-%m-%d")
        })

        # Incrementar contador de serviços do cliente (qtd_cortes)
        cliente_ref = db.collection("barbearias").document(barbearia_id).collection("clientes").document(cliente_selecionado["id"])
        cliente_ref.update({
            "qtd_cortes": cliente_selecionado.get("qtd_cortes", 0) + 1
        })

        st.success("Serviço registrado com sucesso!")
