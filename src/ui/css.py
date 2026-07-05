"""
CSS global do aplicativo
"""
CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">

<style>
:root{
    --bg: #EEF2ED;
    --surface: #FFFFFF;
    --ink: #12241F;
    --muted: #5B6B63;
    --primary: #1F6F5C;
    --primary-dark: #123A30;
    --gold: #C9962E;
    --brick: #B54B3A;
    --line: #D8E0D9;
}

/* Reset e estilos base */
html, body, [class*="css"] { 
    font-family: 'IBM Plex Sans', sans-serif; 
    color: var(--ink); 
}

.stApp { 
    background: var(--bg); 
}

#MainMenu, footer { 
    visibility: hidden; 
}

.block-container { 
    padding-top: 1.5rem; 
    padding-bottom: 3rem; 
    max-width: 1280px; 
}

/* ========================================
   SIDEBAR ESTILOS
   ======================================== */
section[data-testid="stSidebar"] {
    background: var(--primary-dark);
}

section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] .stAlert {
    color: #EAF2EE !important;
}

section[data-testid="stSidebar"] .stSelectbox label { 
    font-weight: 600; 
    letter-spacing: .03em; 
    text-transform: uppercase; 
    font-size: 0.75rem; 
    opacity: .85; 
    color: #FFFFFF !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.08);
    border-color: rgba(255,255,255,0.25);
    border-radius: 8px;
    color: #FFFFFF !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] input {
    color: #FFFFFF !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] input::placeholder {
    color: rgba(255,255,255,0.6) !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] ul li {
    color: #12241F !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] ul li:hover {
    background: rgba(31, 111, 92, 0.1) !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] ul li[aria-selected="true"] {
    background: rgba(31, 111, 92, 0.15) !important;
    color: #12241F !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div:hover {
    background: rgba(255,255,255,0.15);
    border-color: rgba(255,255,255,0.4);
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #EAF2EE !important;
}

section[data-testid="stSidebar"] .caption {
    opacity: 0.7;
    font-size: 0.8rem;
    color: #EAF2EE !important;
}

section[data-testid="stSidebar"] .stSelectbox[disabled] input {
    color: rgba(255,255,255,0.5) !important;
}

/* ========================================
   CAMPOS DE BUSCA NA SIDEBAR
   ======================================== */
section[data-testid="stSidebar"] .stTextInput {
    margin-bottom: 0.2rem;
}

section[data-testid="stSidebar"] .stTextInput label {
    display: none !important;
}

section[data-testid="stSidebar"] .stTextInput input {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 8px;
    color: #EAF2EE !important;
    padding: 0.35rem 0.8rem;
    font-size: 0.8rem;
    transition: all 0.3s ease;
    width: 100%;
}

section[data-testid="stSidebar"] .stTextInput input::placeholder {
    color: rgba(255,255,255,0.3);
    font-size: 0.75rem;
    font-weight: 300;
}

section[data-testid="stSidebar"] .stTextInput input:focus {
    background: rgba(255,255,255,0.12);
    border-color: var(--gold);
    box-shadow: 0 0 0 3px rgba(201, 150, 46, 0.15);
    outline: none;
}

section[data-testid="stSidebar"] .stTextInput input:hover {
    background: rgba(255,255,255,0.09);
    border-color: rgba(255,255,255,0.25);
}

/* Ícone de busca no campo */
section[data-testid="stSidebar"] .stTextInput .stTextInputIcon {
    color: rgba(255,255,255,0.3);
}

/* ========================================
   BOTÃO DE EXPORTAÇÃO NA SIDEBAR
   ======================================== */
section[data-testid="stSidebar"] .stButton button {
    background: var(--gold) !important;
    color: var(--primary-dark) !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.3s ease !important;
    width: 100% !important;
    font-size: 0.9rem !important;
}

section[data-testid="stSidebar"] .stButton button:hover {
    background: #D4A83E !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(201, 150, 46, 0.4);
}

section[data-testid="stSidebar"] .stButton button:active {
    transform: translateY(0px);
}

section[data-testid="stSidebar"] .stDownloadButton button {
    background: var(--gold) !important;
    color: var(--primary-dark) !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.3s ease !important;
    width: 100% !important;
    font-size: 0.9rem !important;
}

section[data-testid="stSidebar"] .stDownloadButton button:hover {
    background: #D4A83E !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(201, 150, 46, 0.4);
}

section[data-testid="stSidebar"] .stDownloadButton button:active {
    transform: translateY(0px);
}

section[data-testid="stSidebar"] .stAlert {
    background: rgba(201, 150, 46, 0.15) !important;
    border-color: var(--gold) !important;
    border-radius: 8px !important;
    padding: 0.8rem !important;
}

section[data-testid="stSidebar"] .stAlert .stAlertIcon {
    color: var(--gold) !important;
}

section[data-testid="stSidebar"] .streamlit-expanderHeader {
    color: #EAF2EE !important;
    opacity: 0.8;
    font-size: 0.85rem;
}

section[data-testid="stSidebar"] .streamlit-expanderHeader:hover {
    opacity: 1;
}

section[data-testid="stSidebar"] .streamlit-expanderContent {
    color: #EAF2EE !important;
}

/* ========================================
   HERO SECTION
   ======================================== */
.hero {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    border-radius: 18px;
    padding: 2.6rem 2.8rem;
    color: #F4F8F5;
    margin-bottom: 1.6rem;
    position: relative;
    overflow: hidden;
    animation: fadeUp .6s ease-out;
}

.hero::after{
    content:"";
    position:absolute; 
    right:-60px; 
    top:-60px;
    width:260px; 
    height:260px; 
    border-radius:50%;
    background: radial-gradient(circle, rgba(201,150,46,0.35), transparent 70%);
}

.hero-eyebrow {
    font-size: 0.8rem;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: var(--gold);
    font-weight: 600;
    margin-bottom: .6rem;
}

.hero-number {
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: clamp(2.6rem, 6vw, 4.2rem);
    line-height: 1;
    margin: 0;
}

.hero-label {
    font-size: 1rem;
    color: #D8E9E1;
    margin-top: .5rem;
}

.hero-sub {
    margin-top: 1rem;
    max-width: 640px;
    color: #CFE3D9;
    font-size: 0.95rem;
    line-height: 1.5;
}

/* ========================================
   CARDS - LARGURA AJUSTADA PARA 5 COLUNAS
   ======================================== */
/* Container dos cards com largura total */
div[data-testid="column"] {
    min-width: 0;
    flex: 1 1 0px;
}

/* Card individual */
.card {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 1.1rem 1rem;
    animation: fadeUp .6s ease-out;
    min-height: 130px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: all 0.3s ease;
    height: 100%;
    width: 100%;
    overflow: hidden;
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}

.card-label {
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: .05em;
    color: var(--muted);
    font-weight: 600;
    line-height: 1.2;
    margin-bottom: 0.2rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.card-value-wrapper {
    display: flex;
    align-items: baseline;
    flex-wrap: wrap;
    gap: 0.15rem;
    min-height: 2.2rem;
    margin-top: 0.2rem;
    overflow: hidden;
}

.card-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--primary-dark);
    line-height: 1.2;
    white-space: nowrap;
    word-break: keep-all;
    display: inline-block;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Ajuste para valores grandes (população) */
.card-value-large {
    font-size: 1.4rem;
}

/* Ajuste para valores pequenos (PIB total) */
.card-value-small {
    font-size: 1rem;
}

.card-unit {
    font-size: 0.7rem;
    color: var(--muted);
    margin-left: 0.15rem;
    font-family: 'IBM Plex Sans', sans-serif;
    white-space: nowrap;
    display: inline-block;
    line-height: 1.2;
    flex-shrink: 0;
}

.card-foot {
    font-size: 0.7rem;
    color: var(--gold);
    margin-top: 0.4rem;
    font-weight: 500;
    line-height: 1.2;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* ========================================
   SECTION TITLES
   ======================================== */
.section-title {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 1.4rem;
    color: var(--primary-dark);
    margin: 1.6rem 0 .8rem 0;
    border-left: 4px solid var(--gold);
    padding-left: .6rem;
}

/* ========================================
   ANIMAÇÕES
   ======================================== */
@keyframes fadeUp {
    from { 
        opacity: 0; 
        transform: translateY(10px); 
    }
    to { 
        opacity: 1; 
        transform: translateY(0); 
    }
}

/* ========================================
   FOLIUM MAP CONTAINER
   ======================================== */
.folium-map-container {
    background: white;
    border-radius: 14px;
    border: 1px solid var(--line);
    overflow: hidden;
    padding: 0;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
}

.folium-map-container:hover {
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}

/* ========================================
   RESPONSIVIDADE
   ======================================== */
@media (max-width: 1200px) {
    .block-container { 
        max-width: 100%; 
        padding-left: 1rem;
        padding-right: 1rem;
    }
}

@media (max-width: 992px) {
    .card-value {
        font-size: 1rem;
    }
    .card-value-large {
        font-size: 1.2rem;
    }
    .card {
        padding: 0.9rem 0.8rem;
        min-height: 110px;
    }
    .card-label {
        font-size: 0.6rem;
    }
    .card-unit {
        font-size: 0.6rem;
    }
    .card-foot {
        font-size: 0.6rem;
    }
}

@media (max-width: 768px) {
    /* Em telas médias, 5 colunas podem virar 2-3 colunas */
    div[data-testid="column"] {
        min-width: 150px;
        flex: 1 1 auto;
    }
    .card {
        padding: 0.8rem 0.6rem;
        min-height: 100px;
    }
    .card-value {
        font-size: 0.9rem;
    }
    .card-value-large {
        font-size: 1rem;
    }
}

@media (max-width: 600px) {
    .hero {
        padding: 1.8rem 1.5rem;
    }
    
    .hero-number {
        font-size: 2.2rem !important;
    }
    
    .card {
        min-height: 90px;
        padding: 0.6rem 0.5rem;
    }
    
    .card-value {
        font-size: 0.8rem;
    }
    
    .card-value-large {
        font-size: 0.9rem;
    }
    
    .card-label {
        font-size: 0.55rem;
    }
    
    .card-unit {
        font-size: 0.55rem;
    }
    
    .card-foot {
        font-size: 0.55rem;
    }
    
    section[data-testid="stSidebar"] {
        padding: 0.5rem !important;
    }
    
    /* Campos de busca em telas pequenas */
    section[data-testid="stSidebar"] .stTextInput input {
        font-size: 0.7rem;
        padding: 0.3rem 0.6rem;
    }
}

/* ========================================
   SCROLLBAR PERSONALIZADA
   ======================================== */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

::-webkit-scrollbar-track {
    background: var(--bg);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: var(--primary);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--primary-dark);
}

::-moz-selection {
    background: var(--gold);
    color: var(--primary-dark);
}

::selection {
    background: var(--gold);
    color: var(--primary-dark);
}

[data-testid="stTooltip"] {
    background: var(--primary-dark) !important;
    color: #EAF2EE !important;
    border-radius: 8px !important;
    padding: 0.5rem 1rem !important;
}
</style>
"""

def get_css() -> str:
    """Retorna o CSS completo do aplicativo"""
    return CSS
