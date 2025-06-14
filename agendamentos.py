import streamlit as st
from datetime import datetime
import uuid

def agendamentos_page(db):
    st.title("📅 Agendamentos")

    barbearia_id = st.session_state["user"]
    agendamentos_ref = db.collection("barbearias").document(barbearia_id).collection("agendamentos")
    clientes_ref = db.collection("barbearias").document(barbearia_id).collection("clientes")
    barbeiros_ref = db.collection("barbearias").document(barbearia_id).collection("barbeiros")

    # Buscar clientes e barbeiros para dropdown
    clientes = {doc.id: doc.to_dict()["nome"] for doc in clientes_ref.stream()}
    barbeiros = {doc.id: doc.to_dict()["nome"] for doc in barbeiros_ref.stream()}

    with st.expander("➕ Agendar novo atendimento"):
        cliente_id = st.selectbox("Cliente", list(clientes.keys()), format_func=lambda x: clientes[x])
        barbeiro_id = st.selectbox("Barbeiro", list(barbeiros.keys()), format_func=lambda x: barbeiros[x])
        data_hora = st.date_input("Data e hora do atendimento", value=datetime.now())
        servico = st.selectbox("Serviço", [
            "Corte de cabelo",
            "Barba",
            "Pezinho",
            "Coloração",
            "Corte + Barba",
            "Coloração + Barba"
        ])

        if st.button("Agendar atendimento"):
            agendamento_id = str(uuid.uuid4())
            agendamentos_ref.document(agendamento_id).set({
                "id": agendamento_id,
                "cliente_id": cliente_id,
                "barbeiro_id": barbeiro_id,
                "data_hora": data_hora.isoformat(),
                "servico": servico,
                "valor": None,
                "foi_realizado": False
            })
            st.success("Agendamento criado com sucesso!")
            st.rerun()

    st.subheader("📋 Próximos atendimentos")
    now = datetime.now().isoformat()
    docs = agendamentos_ref.where("data_hora", ">=", now).order_by("data_hora").stream()

    for doc in docs:
        agendamento = doc.to_dict()
        cliente_nome = clientes.get(agendamento["cliente_id"], "Desconhecido")
        barbeiro_nome = barbeiros.get(agendamento["barbeiro_id"], "Desconhecido")

        with st.container():
            st.markdown(f"""
            **Cliente:** {cliente_nome}  
            **Barbeiro:** {barbeiro_nome}  
            **Data/Hora:** {agendamento['data_hora']}  
            **Serviço:** {agendamento['servico']}  
            **Valor:** {'R$ ' + str(agendamento['valor']) if agendamento['valor'] else 'Não registrado'}  
            **Status:** {"✅ Realizado" if agendamento['foi_realizado'] else "⏳ Pendente"}
            """)

            if not agendamento["foi_realizado"]:
                with st.expander("✔️ Registrar atendimento"):
                    valor = st.number_input(f"Valor cobrado (R$) - {agendamento['id']}", min_value=0.0, step=1.0)
                    if st.button(f"Marcar como realizado - {agendamento['id']}"):
                        doc.reference.update({
                            "valor": valor,
                            "foi_realizado": True
                        })
                        st.success("Atendimento registrado!")
                        st.rerun()

            st.markdown("---")
