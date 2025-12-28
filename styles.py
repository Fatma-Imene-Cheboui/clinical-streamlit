"""
CSS styles for the Clinical Notes Application
"""

MAIN_STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ================= ROOT THEME ================= */
:root {
    --bg-main: #f4f6fb;
    --bg-card: #ffffff;
    --text-main: #2c3e50;
    --text-muted: #8492a6;
}

@media (prefers-color-scheme: dark) {
    :root {
        --bg-main: #0e1117;
        --bg-card: #1e222a;
        --text-main: #e6e9ef;
        --text-muted: #a0a4ab;
    }
}

* {
    font-family: 'Inter', sans-serif;
}

.main {
    background: var(--bg-main);
}

.block-container {
    padding: 1.5rem 2rem !important;
    max-width: 100% !important;
}

/* ================= CARDS ================= */

.cards-container {
    display: flex;
    gap: 0.75rem;
    height: calc(100vh - 320px);
    position: relative;
    overflow: hidden;
}

.note-section {
    background: var(--bg-card);
    color: var(--text-main);
    box-shadow: 0 8px 30px rgba(0,0,0,0.1);
    height: 100%;
    overflow: hidden;
    padding: 1rem;
    border-radius: 16px;
}

/* Desktop cards */
.desktop-card {
    flex: 0 0 calc(33.333% - 0.5rem);
}

/* Mobile cards */
.mobile-card {
    margin-bottom: 0.75rem;
}

/* ================= HEADERS ================= */

.section-header {
    font-weight: 700;
    padding: 0.5rem 0.8rem;
    margin: 0.5rem 0;
    border-radius: 8px;
    display: inline-block;
}

/* Color tags */
.atcd { color:#5D9CEC; background:rgba(93,156,236,0.15); }
.hdm { color:#AC92EC; background:rgba(172,146,236,0.15); }
.exam { color:#4FC1E9; background:rgba(79,193,233,0.15); }
.ecg { color:#ED5565; background:rgba(237,85,101,0.15); }
.ett { color:#FC6E51; background:rgba(252,110,81,0.15); }
.coro { color:#E9573F; background:rgba(233,87,63,0.15); }
.conduite { color:#FFCE54; background:rgba(255,206,84,0.2); }
.cat { color:#A0826D; background:rgba(160,130,109,0.2); }

/* ================= BUTTONS ================= */

.stButton > button {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border-radius: 10px;
    border: none;
    font-weight: 600;
    padding: 0.6rem 1.5rem;
    transition: 0.3s;
}

.stButton > button:hover {
    transform: translateY(-2px);
}

/* ================= INPUTS ================= */

.stSelectbox > div > div,
.stTextArea textarea {
    background: var(--bg-card);
    color: var(--text-main);
    border-radius: 10px;
    border: 1px solid rgba(150,150,150,0.3);
}

label, .stMarkdown {
    color: var(--text-main) !important;
}

/* ================= SCROLLBAR ================= */

::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-thumb {
    background: #667eea;
    border-radius: 10px;
}

/* ================= RESPONSIVE LOGIC ================= */

/* Default = DESKTOP */
.mobile-version {
    display: none;
}

.desktop-version {
    display: block;
}

/* MOBILE OVERRIDE */
@media (max-width: 768px) {

    .desktop-version {
        display: none !important;
    }

    .mobile-version {
        display: block !important;
    }

    .cards-container {
        height: auto;
        flex-direction: column;
    }

    .note-section {
        max-height: none !important;
        overflow: visible !important;
        padding: 0.8rem !important;
    }

    .block-container {
        padding: 0.8rem !important;
    }
}

/* Optional polish */
.mobile-version,
.desktop-version {
    transition: opacity 0.2s ease;
}

</style>

"""