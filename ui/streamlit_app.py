# --- filepath: ui/streamlit_app.py ---
import httpx
import streamlit as st
from datetime import datetime

API = "http://localhost:8000"

st.set_page_config(page_title="FAQ Suggester UI", page_icon="🤖", layout="wide")
st.title("FAQ Suggester • Demo UI")

###############################################################################
# 1) Barra lateral: ver historial completo
###############################################################################
with st.sidebar:
    st.header("Opciones")
    if st.button("📜 Ver historial"):
        resp = httpx.get(f"{API}/history", timeout=30)
        if resp.status_code == 200 and resp.json():
            hist = resp.json()
            with st.expander(f"Historial ({len(hist)} items)", expanded=True):
                st.dataframe(hist, hide_index=True, use_container_width=True,column_order=("timestamp", "query", "suggestion", "added"))
        else:
            st.info("No hay registros aún.")

###############################################################################
# 2) Estado de conversación en sesión
###############################################################################
if "chat" not in st.session_state:
    st.session_state.chat = []

for role, text in st.session_state.chat:
    st.chat_message(role).markdown(text)

###############################################################################
# 3) Campo de entrada (pregunta del ciudadano)
###############################################################################
query = st.chat_input("Escribe la pregunta del ciudadano…")

if query:
    # ── Llamar /suggest ─────────────────────────────────────────────────────
    r = httpx.post(f"{API}/suggest", json={"query": query, "k": 3}, timeout=30)
    if r.status_code != 200:
        st.error("Error en /suggest")
        st.stop()

    data = r.json()
    st.session_state.chat.append(("user", query))

    # ── Mostrar sugerencias como botones ───────────────────────────────────
    with st.chat_message("assistant"):
        st.markdown("### Sugerencias")
        cols = st.columns(len(data["top_k"]))
        for i, cand in enumerate(data["top_k"]):
            label = f"{cand['suggestion']}  \n_(sim: {1-cand['distance']:.2f})_"
            if cols[i].button(label):
                # ── Enviar feedback ─────────────────────────────────────────
                fb = {
                    "query": query,
                    "suggestion": cand["suggestion"],
                    "distance": cand["distance"],
                }
                fb_resp = httpx.post(f"{API}/feedback", json=fb, timeout=30)
                if fb_resp.status_code == 200:
                    res = fb_resp.json()
                    st.success(f"Feedback registrado (added={res['added']})")
                    fb["added"] = res["added"]
                else:
                    st.warning("No se pudo registrar feedback.")

                # Añadir al chat y mostrar resumen de feedback
                st.session_state.chat.append(("assistant", cand["suggestion"]))
                # Mostrar resumen sin forzar recarga
                st.chat_message("system").markdown(f":incoming_envelope: **Feedback**\n\n`{fb}`")

    # Info sobre la siguiente pregunta generada
    st.info(f"Próxima pregunta simulada: **{data['next_question']}**")

