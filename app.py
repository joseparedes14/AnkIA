"""
AnkIA — Aplicación principal Streamlit
Widget para crear tarjetas de vocabulario compatibles con Anki,
con traducción automática vía Ollama (IA local).
"""

import streamlit as st
from utils import anki_manager, context_manager, ollama_client


# ─────────────────────────────────────────────
# Configuración de página
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AnkIA",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────
# CSS Premium inyectado
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Google Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');

    /* ── Variables globales ── */
    :root {
        --accent-1: #667eea;
        --accent-2: #764ba2;
        --bg-dark: #0a0a0f;
        --bg-card: rgba(255, 255, 255, 0.04);
        --bg-card-hover: rgba(255, 255, 255, 0.08);
        --border-subtle: rgba(255, 255, 255, 0.08);
        --border-glow: rgba(102, 126, 234, 0.4);
        --text-primary: #e8e8f0;
        --text-secondary: #8888a0;
        --success: #4ade80;
        --danger: #f87171;
        --warning: #fbbf24;
    }

    /* ── Tipografía general ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
    }

    /* ── Fondo principal ── */
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #12121f 50%, #0a0a0f 100%) !important;
    }

    /* ── Header personalizado ── */
    .ankia-header {
        text-align: center;
        padding: 1.5rem 0 1rem 0;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid var(--border-subtle);
    }
    .ankia-header h1 {
        font-family: 'Outfit', sans-serif !important;
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 !important;
        letter-spacing: -0.02em;
    }
    .ankia-header .subtitle {
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin-top: 0.25rem;
        font-weight: 300;
        letter-spacing: 0.05em;
    }

    /* ── Indicador Ollama ── */
    .ollama-status {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.3rem 0.8rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 500;
        margin-top: 0.5rem;
    }
    .ollama-online {
        background: rgba(74, 222, 128, 0.1);
        border: 1px solid rgba(74, 222, 128, 0.3);
        color: #4ade80;
    }
    .ollama-offline {
        background: rgba(248, 113, 113, 0.1);
        border: 1px solid rgba(248, 113, 113, 0.3);
        color: #f87171;
    }
    .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        display: inline-block;
    }
    .status-dot.online {
        background: #4ade80;
        box-shadow: 0 0 8px rgba(74, 222, 128, 0.6);
        animation: pulse-green 2s ease-in-out infinite;
    }
    .status-dot.offline {
        background: #f87171;
    }

    @keyframes pulse-green {
        0%, 100% { opacity: 1; box-shadow: 0 0 8px rgba(74, 222, 128, 0.6); }
        50% { opacity: 0.6; box-shadow: 0 0 16px rgba(74, 222, 128, 0.3); }
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f1a 0%, #0a0a12 100%) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }
    section[data-testid="stSidebar"] .stMarkdown h2 {
        font-size: 1.1rem !important;
        color: var(--text-secondary) !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 600 !important;
    }

    /* ── Cards de contexto en sidebar ── */
    .context-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 0.8rem 1rem;
        margin: 0.4rem 0;
        cursor: pointer;
        transition: all 0.25s ease;
    }
    .context-card:hover {
        background: var(--bg-card-hover);
        border-color: var(--border-glow);
        transform: translateX(4px);
    }
    .context-card.active {
        background: linear-gradient(135deg, rgba(102,126,234,0.15), rgba(118,75,162,0.15));
        border-color: var(--accent-1);
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.1);
    }
    .context-name {
        font-weight: 600;
        color: var(--text-primary);
        font-size: 0.9rem;
    }
    .context-count {
        color: var(--text-secondary);
        font-size: 0.75rem;
        margin-top: 0.15rem;
    }

    /* ── Glassmorphism panels ── */
    .glass-panel {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        transition: all 0.3s ease;
    }
    .glass-panel:hover {
        border-color: rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    .glass-panel h3 {
        font-family: 'Outfit', sans-serif !important;
        font-size: 1.15rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        margin-bottom: 1rem !important;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* ── Inputs ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-1) !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2),
                    0 0 20px rgba(102, 126, 234, 0.1) !important;
    }

    /* ── Botones principales ── */
    .stButton > button {
        border-radius: 10px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.2rem !important;
        transition: all 0.3s ease !important;
        border: none !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.5) !important;
        transform: translateY(-1px);
    }

    /* ── Tarjeta de vocabulario ── */
    .vocab-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
        animation: fadeInUp 0.4s ease-out;
    }
    .vocab-card:hover {
        background: rgba(255, 255, 255, 0.06);
        border-color: rgba(102, 126, 234, 0.3);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
    }
    .vocab-front {
        font-weight: 600;
        color: var(--text-primary);
        font-size: 1rem;
        margin-bottom: 0.3rem;
    }
    .vocab-translation {
        color: #a78bfa;
        font-size: 0.9rem;
        font-weight: 500;
    }
    .vocab-example {
        color: var(--text-secondary);
        font-size: 0.8rem;
        font-style: italic;
        margin-top: 0.3rem;
        padding-left: 0.5rem;
        border-left: 2px solid rgba(102, 126, 234, 0.3);
    }
    .vocab-index {
        color: rgba(255,255,255,0.15);
        font-size: 0.7rem;
        font-weight: 600;
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(12px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* ── Selectbox ── */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
    }

    /* ── Divider ── */
    hr {
        border-color: rgba(255, 255, 255, 0.06) !important;
        margin: 1rem 0 !important;
    }

    /* ── Toast / Alerts ── */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
    }

    /* ── Badge de número ── */
    .card-count-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 1.5rem;
        height: 1.5rem;
        padding: 0 0.4rem;
        border-radius: 999px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        font-size: 0.7rem;
        font-weight: 700;
    }

    /* ── Shimmer effect para carga ── */
    .shimmer {
        background: linear-gradient(90deg,
            rgba(255,255,255,0.03) 0%,
            rgba(255,255,255,0.08) 50%,
            rgba(255,255,255,0.03) 100%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: 8px;
        height: 2.5rem;
    }
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    /* ── Empty state ── */
    .empty-state {
        text-align: center;
        padding: 3rem 1rem;
        color: var(--text-secondary);
    }
    .empty-state .emoji {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    .empty-state p {
        font-size: 0.9rem;
        max-width: 300px;
        margin: 0 auto;
        line-height: 1.5;
    }

    /* ── Ocultar elementos de Streamlit ── */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Inicialización de estado
# ─────────────────────────────────────────────
if "active_context" not in st.session_state:
    st.session_state.active_context = None
if "ollama_status" not in st.session_state:
    st.session_state.ollama_status = None
if "translation_result" not in st.session_state:
    st.session_state.translation_result = None
# Modelos ya no se seleccionan en la UI (fijo a translategemma)


# ─────────────────────────────────────────────
# Comprobar estado de Ollama (una vez por sesión o al refrescar)
# ─────────────────────────────────────────────
def refresh_ollama_status():
    status = ollama_client.check_status()
    st.session_state.ollama_status = status["available"]
    pass # No necesitamos guardar los modelos


if st.session_state.ollama_status is None:
    refresh_ollama_status()


# ─────────────────────────────────────────────
# SIDEBAR — Contextos
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📚 Contextos")

    # Botón para refrescar Ollama
    col_refresh, col_status = st.columns([1, 2])
    with col_refresh:
        if st.button("🔄", help="Refrescar estado de Ollama", key="refresh_ollama"):
            refresh_ollama_status()
            st.rerun()

    with col_status:
        if st.session_state.ollama_status:
            st.markdown(
                '<div class="ollama-status ollama-online">'
                '<span class="status-dot online"></span> Ollama conectado'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="ollama-status ollama-offline">'
                '<span class="status-dot offline"></span> Ollama offline'
                '</div>',
                unsafe_allow_html=True,
            )

    st.divider()

    # Modelo fijo, no mostramos selector
    # Lista de contextos existentes
    contexts = context_manager.list_contexts()

    if contexts:
        for ctx in contexts:
            is_active = st.session_state.active_context == ctx["name"]
            col_ctx, col_del = st.columns([5, 1])

            with col_ctx:
                active_class = "active" if is_active else ""
                st.markdown(
                    f'<div class="context-card {active_class}">'
                    f'  <div class="context-name">📖 {ctx["name"]}</div>'
                    f'  <div class="context-count">{ctx["card_count"]} tarjetas</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                if st.button(
                    "Seleccionar" if not is_active else "✓ Activo",
                    key=f"select_{ctx['name']}",
                    disabled=is_active,
                    use_container_width=True,
                ):
                    st.session_state.active_context = ctx["name"]
                    st.session_state.translation_result = None
                    st.rerun()

            with col_del:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"delete_{ctx['name']}", help=f"Eliminar {ctx['name']}"):
                    context_manager.delete_context(ctx["name"])
                    if st.session_state.active_context == ctx["name"]:
                        st.session_state.active_context = None
                    st.rerun()
    else:
        st.markdown(
            '<div class="empty-state">'
            '<div class="emoji">📭</div>'
            '<p>No hay contextos creados aún. ¡Crea tu primer vocabulario!</p>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # Crear nuevo contexto
    st.markdown("### ➕ Nuevo contexto")
    new_context_name = st.text_input(
        "Nombre del contexto",
        placeholder="Ej: Adjetivos C1 Ingles-Aleman",
        key="new_context_input",
    )

    new_context_description = st.text_area(
        "Descripción (opcional)",
        placeholder="Ej: vocabulario de cocina, para mejorar recomendaciones",
        key="new_context_description",
        height=68,
    )
    
    col_lang1, col_lang2 = st.columns(2)
    langs = ["Español", "Inglés", "Alemán", "Francés", "Italiano", "Portugués", "Japonés", "Chino", "Coreano", "Ruso", "Árabe"]
    with col_lang1:
        new_source_lang = st.selectbox("De", langs, index=1, key="new_source_lang")
    with col_lang2:
        new_target_lang = st.selectbox("A", langs, index=0, key="new_target_lang")

    levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
    new_level = st.selectbox("Nivel CEFR", levels, index=3, key="new_level")

    if st.button("Crear contexto", key="create_context", use_container_width=True, type="primary"):
        if new_context_name.strip():
            try:
                result = context_manager.create_context(new_context_name, new_source_lang, new_target_lang, new_level, new_context_description.strip())
                st.session_state.active_context = result["name"]
                st.toast(f"✅ Contexto '{result['name']}' creado", icon="📚")
                st.rerun()
            except ValueError as e:
                st.error(str(e))
        else:
            st.warning("Escribe un nombre para el contexto.")


# ─────────────────────────────────────────────
# MAIN — Header
# ─────────────────────────────────────────────
st.markdown(
    '<div class="ankia-header">'
    '  <h1>🧠 AnkIA</h1>'
    '  <div class="subtitle">Tarjetas de vocabulario inteligentes con IA local</div>'
    '</div>',
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# MAIN — Zona de entrada de tarjetas
# ─────────────────────────────────────────────
if st.session_state.active_context:
    deck_path = context_manager.get_deck_path(st.session_state.active_context)
    ctx_meta = context_manager.get_context_metadata(st.session_state.active_context)
    source_lang = ctx_meta.get("source_lang", "Español")
    target_lang = ctx_meta.get("target_lang", "Alemán")
    level = ctx_meta.get("level", "B2")

    # Panel de contexto activo
    description = ctx_meta.get("description", "")
    desc_html = f'<div style="font-size: 0.8em; color: var(--text-secondary); margin-top: 0.3rem;">📌 {description}</div>' if description else ""
    st.markdown(
        f'<div class="glass-panel">'
        f'  <h3>📝 Contexto Activo — <span style="color: #a78bfa;">{st.session_state.active_context}</span> '
        f'  <span style="font-size: 0.8em; color: var(--text-secondary);">({source_lang} → {target_lang} | {level})</span></h3>'
        f'  {desc_html}'
        f'</div>',
        unsafe_allow_html=True,
    )

    tab_manual, tab_ia = st.tabs(["➕ Añadir Manual", "✨ Descubrir con IA"])

    with tab_manual:
        # Feedback si Ollama no está conectado
        if not st.session_state.ollama_status:
            st.warning("⚠️ Ollama no disponible — comprueba la conexión desde el panel lateral.")

        # Flujo minimalista: Input de chat
        word_input = st.chat_input(
            f"Escribe la palabra en {source_lang} y pulsa Enter...",
            key="word_input",
        )

        if word_input and word_input.strip():
            if not st.session_state.ollama_status:
                st.error("No se puede traducir sin conexión a Ollama.")
            else:
                with st.spinner(f"🔄 Consultando a la IA y guardando '{word_input.strip()}'..."):
                    result = ollama_client.translate_word(
                        word=word_input.strip(),
                        source_lang=source_lang,
                        target_lang=target_lang,
                        context_name=st.session_state.active_context,
                        context_description=ctx_meta.get("description", ""),
                    )
                    
                    if result["success"]:
                        if anki_manager.card_exists(deck_path, result["front"]):
                            st.warning(f"⚠️ Ya existe una tarjeta con el frente '{result['front']}'.")
                        else:
                            anki_manager.add_card(deck_path, result["front"], result["translation"], result["example"])
                            st.toast(f"✅ Tarjeta añadida: {result['front']}", icon="🎴")
                            st.rerun()
                    else:
                        st.error(f"Error de la IA: {result['error']}")

    with tab_ia:
        st.markdown("### 🎲 Recomendador de Vocabulario")
        st.markdown(f"La IA generará nuevas tarjetas del nivel **{level}** que aún no tengas en este mazo.")
        
        amount = st.slider("Cantidad de tarjetas a generar:", 1, 20, 5)
        
        if st.button("🚀 Generar Recomendaciones", type="primary", use_container_width=True):
            if not st.session_state.ollama_status:
                st.error("No se puede generar sin conexión a Ollama.")
            else:
                existing_cards = anki_manager.read_cards(deck_path)
                existing_words = [c["front"] for c in existing_cards]
                
                with st.spinner(f"🔄 La IA está pensando en {amount} palabras nuevas (puede tardar unos 10-20 segundos)..."):
                    res = ollama_client.generate_recommendations(
                        amount=amount,
                        existing_words=existing_words,
                        context_name=st.session_state.active_context,
                        level=level,
                        source_lang=source_lang,
                        target_lang=target_lang,
                        context_description=ctx_meta.get("description", ""),
                    )
                    
                    if res["success"]:
                        st.session_state.pending_recommendations = res["recommendations"]
                    else:
                        st.error(f"Error de la IA: {res['error']}")
        
        if st.session_state.get("pending_recommendations"):
            st.markdown("---")
            st.markdown("#### 🧐 Revisa y selecciona las tarjetas:")
            
            selected_indices = []
            for i, rec in enumerate(st.session_state.pending_recommendations):
                label = f"**{rec.get('front', '')}** ➔ {rec.get('translation', '')} *(Ej: {rec.get('example', '')})*"
                if st.checkbox(label, value=True, key=f"chk_rec_{i}"):
                    selected_indices.append(i)
                    
            if st.button("💾 Aprobar y Guardar Seleccionadas", type="primary"):
                if not selected_indices:
                    st.warning("No has seleccionado ninguna tarjeta.")
                else:
                    saved_count = 0
                    for i in selected_indices:
                        rec = st.session_state.pending_recommendations[i]
                        anki_manager.add_card(deck_path, rec["front"], rec["translation"], rec["example"])
                        saved_count += 1
                    
                    st.session_state.pending_recommendations = []
                    st.toast(f"✅ Se guardaron {saved_count} nuevas tarjetas en el mazo.", icon="🎴")
                    st.rerun()

    # ─────────────────────────────────────────────
    # MAIN — Feed de tarjetas del contexto activo
    # ─────────────────────────────────────────────
    st.markdown("---")
    cards = anki_manager.read_cards(deck_path)

    col_title, col_download = st.columns([4, 2])
    with col_title:
        st.markdown(
            f'<div class="glass-panel" style="margin-bottom: 1.2rem; padding: 1rem 1.5rem;">'
            f'  <h3 style="margin-bottom: 0 !important;">📋 Tarjetas <span class="card-count-badge">{len(cards)}</span></h3>'
            f'</div>',
            unsafe_allow_html=True,
        )
    
    with col_download:
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        if cards:
            with open(deck_path, "r", encoding="utf-8") as f:
                deck_content = f.read()
            st.download_button(
                label="📥 Descargar .txt para Anki",
                data=deck_content,
                file_name=f"{st.session_state.active_context}.txt",
                mime="text/plain",
                use_container_width=True,
                type="primary",
            )

    if cards:
        # Mostrar tarjetas de más reciente a más antigua
        for card in reversed(cards):
            col_card, col_action = st.columns([6, 1])

            with col_card:
                st.markdown(
                    f'<div class="vocab-card">'
                    f'  <div class="vocab-index">#{card["index"] + 1}</div>'
                    f'  <div class="vocab-front">{card["front"]}</div>'
                    f'  <div class="vocab-translation">{card["translation"]}</div>'
                    f'  <div class="vocab-example">"{card["example"]}"</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            with col_action:
                st.markdown("<br><br>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_card_{card['index']}", help="Eliminar tarjeta"):
                    anki_manager.delete_card(deck_path, card["index"])
                    st.toast("🗑️ Tarjeta eliminada", icon="❌")
                    st.rerun()
    else:
        st.markdown(
            '<div class="empty-state">'
            '<div class="emoji">✨</div>'
            '<p>Aún no hay tarjetas en este contexto. ¡Añade tu primera palabra!</p>'
            '</div>',
            unsafe_allow_html=True,
        )

else:
    # No hay contexto seleccionado
    st.markdown(
        '<div class="empty-state" style="padding: 5rem 1rem;">'
        '<div class="emoji">👈</div>'
        '<p style="font-size: 1.1rem;">Selecciona o crea un contexto en el panel lateral para empezar a añadir tarjetas.</p>'
        '</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="text-align:center; color: rgba(255,255,255,0.15); font-size: 0.75rem;">'
    'AnkIA v0.1 — Tarjetas de vocabulario con IA local'
    '</p>',
    unsafe_allow_html=True,
)
