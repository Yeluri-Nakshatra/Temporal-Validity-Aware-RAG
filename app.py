"""Streamlit demo for TVA-RAG.  Run:  streamlit run app.py"""
import sys, pathlib, datetime as dt
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "src"))
import streamlit as st
from tva_rag.corpus import load_benchmark, load_documents
from tva_rag.pipeline import TVARAG
from tva_rag.generator import get_client

st.set_page_config(page_title="TVA-RAG demo", layout="wide")
st.title("Temporal-Validity-Aware RAG")
st.caption("Ask a question, pick a reference date, and compare naive RAG with TVA-RAG on the same retrieved documents.")


@st.cache_resource
def load_system():
    bench = load_benchmark()
    docs = load_documents(bench, "mixed")
    return TVARAG(docs, get_client(), device="cuda", k=5), bench


system, bench = load_system()
col1, col2 = st.columns([3, 1])
with col1:
    question = st.text_input("Question", "What GST rate applies to individual health insurance premiums in India?")
with col2:
    t = st.date_input("Reference date", dt.date(2026, 1, 1))
model = st.selectbox("Model", ["llama3.1:8b", "qwen2.5:7b", "llama3.2:3b", "qwen3.5:35b"])

if st.button("Run"):
    left, right = st.columns(2)
    with left:
        st.subheader("Naive RAG")
        r = system.answer(question, t, "naive", model)
        st.markdown(f"**Answer:** {r['answer']}")
        with st.expander("Raw output and context"):
            st.text(r["raw"]); st.text(r["prompt"])
    with right:
        st.subheader("TVA-RAG")
        r = system.answer(question, t, "tva", model)
        st.markdown(f"**Answer:** {r['answer']}")
        st.markdown(f"**Valid from:** {r['valid_from']}  |  **Basis:** {r['basis']}")
        st.markdown("**Evidence status**")
        for doc_id, status in r["statuses"].items():
            colour = {"CURRENT": "green", "SUPERSEDED": "red", "UNVERIFIED": "orange", "FUTURE": "grey"}.get(status, "blue")
            meta = system.meta[doc_id]
            st.markdown(f"- :{colour}[{status}] `{doc_id}` dated {meta.effective or meta.pub_date or 'unknown'} (confidence {meta.confidence:.2f})")
        with st.expander("Raw output and annotated context"):
            st.text(r["raw"]); st.text(r["prompt"])
