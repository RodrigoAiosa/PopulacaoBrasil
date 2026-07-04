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

html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; color: var(--ink); }
.stApp { background: var(--bg); }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1180px; }

section[data-testid="stSidebar"] {
    background: var(--primary-dark);
}
section[data-testid="stSidebar"] * { color: #EAF2EE !important; }
section[data-testid="stSidebar"] .stSelectbox label { 
    font-weight: 600; 
    letter-spacing: .03em; 
    text-transform: uppercase; 
    font-size: 0.75rem; 
    opacity: .85; 
}
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.08);
    border-color: rgba(255,255,255,0.25);
}

/* Hero */
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
    position:absolute; right:-60px; top:-60px;
    width:260px; height:260px; border-radius:50%;
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

/* Cards */
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

/* Section titles */
.section-title {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 1.4rem;
    color: var(--primary-dark);
    margin: 1.6rem 0 .8rem 0;
    border-left: 4px solid var(--gold);
    padding-left: .6rem;
}

/* Animations */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Folium map container */
.folium-map-container {
    background: white;
    border-radius: 14px;
    border: 1px solid var(--line);
    overflow: hidden;
    padding: 0;
    margin-bottom: 1rem;
}

/* Responsive adjustments */
@media (max-width: 900px) { 
    .card-grid { grid-template-columns: repeat(2, 1fr); } 
}
</style>
"""

def get_css() -> str:
    """Retorna o CSS completo do aplicativo"""
    return CSS
