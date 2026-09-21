from pathlib import Path
import os
import time
import streamlit as st
from dotenv import load_dotenv

from database import ExpoDatabase
from rag_engine import RAGEngine
from assistant_engine import ExpoAssistant

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")

st.set_page_config(
    page_title="Assistente ao Expositor | ExpoCatólica 2026",
    page_icon="💬",
    layout="wide",
)

@st.cache_resource
def services():
    db = ExpoDatabase(ROOT / "dados")
    rag = RAGEngine(ROOT / "documentos", ROOT / "chroma_db")
    assistant = ExpoAssistant(db, rag, ROOT / "system_prompt.txt")
    return db, rag, assistant

db, rag, assistant = services()

st.title("Assistente ao Expositor — ExpoCatólica 2026")
st.caption("Protótipo acadêmico | AI Factory: Building Intelligent Systems")

with st.sidebar:
    st.header("Configuração")
    provider = st.selectbox(
        "Modo de resposta",
        ["Automático", "OpenAI", "Local (sem API)"],
        help="Automático usa OpenAI se houver chave no .env; caso contrário usa o modo local.",
    )
    role = st.radio("Perfil", ["Organização", "Expositor"], horizontal=True)

    requester_id = None
    if role == "Expositor":
        exhibitors = db.exhibitors()
        labels = {x["nome"]: x["id"] for x in exhibitors}
        chosen = st.selectbox("Expositor de demonstração", list(labels.keys()))
        requester_id = labels[chosen]
        st.info("Neste perfil, consultas estruturadas de outros expositores são bloqueadas.")

    st.divider()
    st.write(f"**RAG:** {rag.backend}")
    has_key = bool(os.getenv("OPENAI_API_KEY", "").strip())
    st.write(f"**Chave de LLM:** {'configurada' if has_key else 'não configurada'}")

    st.divider()
    st.markdown("**Perguntas para testar**")
    st.caption("RAG")
    st.code("Quais são as datas e horários de montagem?")
    st.code("Até quando posso solicitar energia adicional e hidráulica?")
    st.code("Posso compartilhar meu estande com outra marca?")
    st.caption("Dados")
    st.code("Qual é o estande e a metragem da Editora Caminho Novo?")
    st.code("Quais pendências estão abertas para a Turismo Peregrino Brasil?")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Olá! Posso consultar regras e prazos da ExpoCatólica 2026 e também "
                "os dados fictícios de expositores, estandes e pendências usados nesta demonstração."
            ),
            "sources": [],
            "mode": "inicial",
        }
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("Fontes"):
                for src in msg["sources"]:
                    st.write(f"- {src}")
        if msg.get("mode") and msg["role"] == "assistant":
            st.caption(f"Modo: {msg['mode']}")

question = st.chat_input("Digite sua pergunta sobre a ExpoCatólica 2026")

def stream_words(text):
    parts = text.split(" ")
    for i, part in enumerate(parts):
        yield part + (" " if i < len(parts)-1 else "")
        time.sleep(0.012)

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Consultando documentos e dados..."):
            answer, sources, mode = assistant.answer(
                question,
                provider=provider,
                role=role,
                requester_id=requester_id,
            )
        st.write_stream(stream_words(answer))
        if sources:
            with st.expander("Fontes"):
                for src in sources:
                    st.write(f"- {src}")
        st.caption(f"Modo: {mode}")

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": sources, "mode": mode}
    )

st.divider()
st.caption(
    "Dados tabulares são fictícios e destinados à demonstração acadêmica. "
    "O protótipo não substitui o Manual do Expositor, o Regulamento Geral ou orientações oficiais da organização."
)
