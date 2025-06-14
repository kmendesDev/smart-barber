import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

from servicos import realizar_servico_page
from auth import login_form, criar_barbearia
from dashboard import dashboard
from clientes import clientes_page
from barbeiros import barbeiros_page
from agendamentos import agendamentos_page
from aniversariantes import aniversariantes_page

# Configuração do layout da página
st.set_page_config(
    page_title="Smart Barber 💈",
    page_icon="💈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para carregar CSS customizado
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Inicializa Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("smart-barber-firebase.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Estado inicial
if "user" not in st.session_state:
    st.session_state["user"] = None

st.sidebar.title("Bem-vindo!")

if st.session_state["user"]:
    st.sidebar.markdown(f"Logado como: **{st.session_state.get('barbearia_nome', '')}**")
    if st.sidebar.button("Sair"):
        st.session_state["user"] = None
        st.session_state["barbearia_nome"] = None
        st.rerun()

    # Navegação principal
    pagina = st.sidebar.selectbox("Navegar para", [
        "Dashboard", "Realizar Serviço", "Clientes", "Barbeiros", "Agendamentos", "Aniversariantes"
    ])

    if pagina == "Dashboard":
        dashboard(db)
    elif pagina == "Realizar Serviço":
        realizar_servico_page(db)
    elif pagina == "Clientes":
        clientes_page(db)
    elif pagina == "Barbeiros":
        barbeiros_page(db)
    elif pagina == "Agendamentos":
        agendamentos_page(db)
    elif pagina == "Aniversariantes":
        aniversariantes_page(db)

else:
    opcao = st.sidebar.radio("Você já tem cadastro?", ["Fazer login", "Criar barbearia"])
    if opcao == "Fazer login":
        login_form(db)
    else:
        criar_barbearia(db)
