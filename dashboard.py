import streamlit as st
from datetime import datetime

def dashboard(db):
    st.title("📊 Dashboard da Barbearia")

    barbearia_id = st.session_state["user"]

    clientes_ref = db.collection("barbearias").document(barbearia_id).collection("clientes")
    barbeiros_ref = db.collection("barbearias").document(barbearia_id).collection("barbeiros")
    agendamentos_ref = db.collection("barbearias").document(barbearia_id).collection("agendamentos")
    servicos_ref = db.collection("barbearias").document(barbearia_id).collection("servicos")

    # Totais básicos
    total_clientes = len(list(clientes_ref.stream()))
    total_barbeiros = len(list(barbeiros_ref.stream()))

    # Data de hoje
    hoje_str = datetime.now().strftime("%Y-%m-%d")

    # Totais dos agendamentos
    total_agendados_hoje = 0
    total_realizados_hoje = 0
    total_valor_agendamentos_hoje = 0.0

    for doc in agendamentos_ref.stream():
        ag = doc.to_dict()
        data_hora = ag.get("data_hora", "")[:10]
        if data_hora == hoje_str:
            total_agendados_hoje += 1
            if ag.get("foi_realizado"):
                total_realizados_hoje += 1
                total_valor_agendamentos_hoje += ag.get("valor", 0)

    # Totais dos serviços realizados hoje
    total_servicos_hoje = 0
    total_valor_servicos_hoje = 0.0

    for doc in servicos_ref.stream():
        serv = doc.to_dict()
        data = serv.get("data", "")
        if data == hoje_str:
            total_servicos_hoje += 1
            total_valor_servicos_hoje += serv.get("valor", 0.0)

    # Exibição
    col1, col2 = st.columns(2)
    with col1:
        st.metric("👥 Clientes cadastrados", total_clientes)
        st.metric("✂️ Barbeiros cadastrados", total_barbeiros)
    with col2:
        st.metric("📅 Agendamentos hoje", total_agendados_hoje)
        st.metric("✅ Serviços realizados hoje", f"R$ {total_valor_agendamentos_hoje:.2f}")

    st.markdown("---")
    st.metric("💰 Total arrecadado em agendamentos hoje", f"R$ {total_valor_agendamentos_hoje:.2f}")
    st.metric("💵 Total arrecadado em serviços hoje", f"R$ {total_valor_servicos_hoje:.2f}")
