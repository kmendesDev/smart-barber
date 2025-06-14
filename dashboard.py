import streamlit as st
from datetime import datetime
import pandas as pd
import altair as alt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
import calendar


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
    hoje = datetime.now().date()
    hoje_str = hoje.strftime("%Y-%m-%d")

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

    # Dicionário para gráfico
    valores_por_data = {}

    for doc in servicos_ref.stream():
        serv = doc.to_dict()
        data_str = serv.get("data", "")
        valor = serv.get("valor", 0.0)

        # Gráfico
        try:
            data = datetime.strptime(data_str, "%Y-%m-%d").date()
        except:
            continue

        if data == hoje:
            total_servicos_hoje += 1
            total_valor_servicos_hoje += valor

        if data in valores_por_data:
            valores_por_data[data] += valor
        else:
            valores_por_data[data] = valor

    # Exibição dos KPIs
    col1, col2 = st.columns(2)
    with col1:
        st.metric("👥 Clientes cadastrados", total_clientes)
        st.metric("✂️ Barbeiros cadastrados", total_barbeiros)
    with col2:
        st.metric("📅 Agendamentos hoje", total_agendados_hoje)
        st.metric("✅ Serviços realizados hoje", f"{total_servicos_hoje}")

    st.markdown("---")
    st.metric("💵 Total em serviços hoje", f"R$ {total_valor_servicos_hoje:.2f}")

    # Gráfico dos últimos 30 dias
    st.markdown("## 📈 Receita de Serviços (últimos 30 dias)")
    df_servicos = pd.DataFrame(list(valores_por_data.items()), columns=["Data", "Valor"])
    df_servicos["Data"] = pd.to_datetime(df_servicos["Data"])
    df_servicos = df_servicos.sort_values("Data")

    trinta_dias_atras = hoje - pd.Timedelta(days=30)
    df_filtrado = df_servicos[df_servicos["Data"].dt.date >= trinta_dias_atras]

    if not df_filtrado.empty:
        grafico = alt.Chart(df_filtrado).mark_line(point=True).encode(
            x=alt.X('Data:T', title='Data'),
            y=alt.Y('Valor:Q', title='Valor Arrecadado (R$)'),
            tooltip=['Data:T', 'Valor:Q']
        ).properties(
            width=700,
            height=400
        ).interactive()

        st.altair_chart(grafico)
    else:
        st.info("Ainda não há dados de serviços nos últimos 30 dias.")
        # Botão para exportar PDF
        # Botão para exportar PDF
    if st.button("📄 Exportar Extrato em PDF"):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        nome_barbearia = db.collection("barbearias").document(barbearia_id).get().to_dict().get("nome", "Barbearia")
        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, height - 50, f"Extrato Financeiro - {nome_barbearia}")
        c.setFont("Helvetica", 12)
        c.drawString(40, height - 70, f"Período: {trinta_dias_atras.strftime('%d/%m/%Y')} a {hoje.strftime('%d/%m/%Y')}")

        y = height - 100

        # Cálculo geral e por barbeiro
        barbeiros = list(barbeiros_ref.stream())
        total_servicos_30_dias = 0
        total_geral_valor = 0.0
        faturamento_barbeiros = {}

        for b in barbeiros:
            barbeiro = b.to_dict()
            nome = barbeiro.get("nome", "Sem nome")
            total = 0.0
            for doc in servicos_ref.where("barbeiro_id", "==", b.id).stream():
                s = doc.to_dict()
                try:
                    data = datetime.strptime(s.get("data", ""), "%Y-%m-%d").date()
                    if trinta_dias_atras <= data <= hoje:
                        valor = s.get("valor", 0.0)
                        total += valor
                        total_geral_valor += valor
                        total_servicos_30_dias += 1
                except:
                    continue
            faturamento_barbeiros[nome] = total

        ticket_medio = (total_geral_valor / total_servicos_30_dias) if total_servicos_30_dias > 0 else 0.0
        destaque = max(faturamento_barbeiros.items(), key=lambda x: x[1]) if faturamento_barbeiros else ("-", 0.0)

        # Bloco: Resumo geral
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, "📌 Resumo Geral:")
        y -= 20
        c.setFont("Helvetica", 12)
        c.drawString(60, y, f"- Total de serviços realizados: {total_servicos_30_dias}")
        y -= 20
        c.drawString(60, y, f"- Valor arrecadado: R$ {total_geral_valor:.2f}")
        y -= 20
        c.drawString(60, y, f"- Ticket médio: R$ {ticket_medio:.2f}")
        y -= 20
        c.drawString(60, y, f"- Destaque do mês: {destaque[0]} (R$ {destaque[1]:.2f})")

        # 1. Acumulado por barbeiro
        y -= 30
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, "💈 Total de serviços por barbeiro:")
        y -= 20
        for nome, valor in faturamento_barbeiros.items():
            c.setFont("Helvetica", 12)
            c.drawString(60, y, f"- {nome}: R$ {valor:.2f}")
            y -= 20

        # 2. Histórico por dia
        y -= 10
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, "📆 Histórico diário:")
        y -= 20

        for _, row in df_filtrado.iterrows():
            data = row["Data"].date()
            valor = row["Valor"]
            dia_semana = calendar.day_name[data.weekday()]
            linha = f"{data.strftime('%d/%m/%Y')} ({dia_semana}): R$ {valor:.2f}"
            if y < 50:
                c.showPage()
                y = height - 50
            c.setFont("Helvetica", 12)
            c.drawString(60, y, linha)
            y -= 20

        c.save()
        buffer.seek(0)

        st.download_button(
            label="📥 Baixar PDF",
            data=buffer,
            file_name=f"extrato_{nome_barbearia.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )

