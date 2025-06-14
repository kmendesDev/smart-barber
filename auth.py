import streamlit as st
import hashlib
import uuid

def hash_password(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def criar_barbearia(db):
    st.title("Cadastrar Nova Barbearia")

    nome = st.text_input("Nome da barbearia")
    email = st.text_input("Email para login")
    senha = st.text_input("Senha", type="password")
    telefone = st.text_input("Telefone")
    endereco = st.text_area("Endereço (opcional)")

    if st.button("Criar barbearia"):
        if nome and email and senha:
            barbearia_id = str(uuid.uuid4())
            senha_hash = hash_password(senha)

            doc_ref = db.collection("barbearias").document(barbearia_id)
            doc_ref.set({
                "id": barbearia_id,
                "nome": nome,
                "email": email,
                "senha_hash": senha_hash,
                "telefone": telefone,
                "endereco": endereco
            })

            st.success(f"Barbearia {nome} criada com sucesso! Faça o login.")
        else:
            st.warning("Preencha todos os campos obrigatórios.")

def login_form(db):
    st.title("Login da Barbearia")

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if not email or not senha:
            st.warning("Preencha email e senha.")
            return

        senha_hash = hash_password(senha)

        barbearias = db.collection("barbearias").where("email", "==", email).stream()

        barbearia = None
        for b in barbearias:
            barbearia = b
            break

        if barbearia:
            data = barbearia.to_dict()
            if data.get("senha_hash") == senha_hash:
                st.session_state["user"] = data["id"]
                st.session_state["barbearia_nome"] = data["nome"]
                st.success(f"Login bem-sucedido! Bem-vindo(a), {data['nome']}")
            else:
                st.error("Senha incorreta.")
        else:
            st.error("Barbearia não encontrada.")
