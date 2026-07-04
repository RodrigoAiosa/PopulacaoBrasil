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
    max-width: 1180px; 
}

/* ========================================
   SIDEBAR ESTILOS
   ======================================== */
section[data-testid="stSidebar"] {
    background: var(--primary-dark);
}

section[data-testid="stSidebar"] * { 
    color: #EAF2EE !important; 
}

/* Labels dos selects na sidebar */
section[data-testid="stSidebar"] .stSelectbox label { 
    font-weight: 600; 
    letter-spacing: .03em; 
    text-transform: uppercase; 
    font-size: 0.75rem; 
    opacity: .85; 
}

/* Select boxes na sidebar */
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.08);
    border-color: rgba(255,255,255,0.25);
    border-radius: 8px;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div:hover {
    background: rgba(255,255,255,0.15);
    border-color: rgba(255,255,255,0.4);
}

/* Headers na sidebar */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #EAF2EE !important;
}

/* Caption na sidebar */
section[data-testid="stSidebar"] .caption {
    opacity: 0.7;
    font-size: 0.8rem;
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

/* Download button na sidebar */
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

/* Export section divider */
.sidebar-export-divider {
    border-top: 1px solid rgba(255,255,255,0.1);
    margin: 1rem 0;
}

/* ========================================
   LINKEDIN FOOTER NA SIDEBAR
   ======================================== */
.sidebar-linkedin-footer {
    text-align: center;
    padding: 15px 0 10px 0;
    margin-top: 10px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-linkedin-footer a {
    color: #EAF2EE !important;
    text-decoration: none !important;
    font-size: 13px;
    opacity: 0.7;
    transition: all 0.3s ease;
    display: inline-block;
}

.sidebar-linkedin-footer a:hover {
    opacity: 1;
    color: #FFFFFF !important;
    transform: scale(1.05);
}

.sidebar-linkedin-footer .linkedin-icon {
    display: block;
    margin: 0 auto 6px auto;
    transition: all 0.3s ease;
}

.sidebar-linkedin-footer .linkedin-icon:hover {
    transform: scale(1.1);
}

.sidebar-linkedin-footer .linkedin-text {
    font-size: 12px;
    opacity: 0.6;
    letter-spacing: 0.3px;
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
   CARDS
   ======================================== */
.card {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 1.3rem 1.4rem;
    animation: fadeUp .6s ease-out;
    min-height: 148px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: all 0.3s ease;
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}

.card-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: .06em;
    color: var(--muted);
    font-weight: 600;
    line-height: 1.3;
}

.card-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.4rem;
    font-weight: 600;
    color: var(--primary-dark);
    margin-top: .3rem;
    line-height: 1.25;
    white-space: normal;
}

.card-unit {
    font-size: 0.78rem;
    color: var(--muted);
    margin-left: .3rem;
    font-family: 'IBM Plex Sans', sans-serif;
    white-space: nowrap;
}

.card-foot {
    font-size: 0.78rem;
    color: var(--gold);
    margin-top: .5rem;
    font-weight: 500;
    line-height: 1.3;
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

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
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
   WARNINGS E INFOS NA SIDEBAR
   ======================================== */
section[data-testid="stSidebar"] .stAlert {
    background: rgba(201, 150, 46, 0.15) !important;
    border-color: var(--gold) !important;
    border-radius: 8px !important;
    padding: 0.8rem !important;
}

section[data-testid="stSidebar"] .stAlert .stAlertIcon {
    color: var(--gold) !important;
}

section[data-testid="stSidebar"] .stAlert .stMarkdown {
    color: #EAF2EE !important;
}

/* ========================================
   EXPANDER NA SIDEBAR
   ======================================== */
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
   RESPONSIVIDADE
   ======================================== */
@media (max-width: 900px) { 
    .card-grid { 
        grid-template-columns: repeat(2, 1fr); 
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
        min-height: 120px;
        padding: 1rem;
    }
    
    .card-value {
        font-size: 1.1rem;
    }
    
    section[data-testid="stSidebar"] {
        padding: 0.5rem !important;
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

/* ========================================
   SELECIONADORES DE TEXTO
   ======================================== */
::selection {
    background: var(--gold);
    color: var(--primary-dark);
}

/* ========================================
   TOOLTIP PERSONALIZADO
   ======================================== */
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
