"""
CSS styles for the Clinical Notes Application
"""

MAIN_STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

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

.login-title {
    color: var(--text-main);
    margin: 1rem 0 0.5rem 0;
    font-weight: 700;
}

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
    flex: 0 0 calc(33.333% - 0.5rem);
    height: 100%;
    overflow-y: auto;
    padding: 1rem;
    border-radius: 16px;
}

.section-header {
    font-weight: 700;
    padding: 0.5rem 0.8rem;
    margin: 0.5rem 0;
    border-radius: 8px;
    display: inline-block;
}

.atcd { color:#5D9CEC; background:rgba(93,156,236,0.15); }
.hdm { color:#AC92EC; background:rgba(172,146,236,0.15); }
.exam { color:#4FC1E9; background:rgba(79,193,233,0.15); }
.ecg { color:#ED5565; background:rgba(237,85,101,0.15); }
.ett { color:#FC6E51; background:rgba(252,110,81,0.15); }
.coro { color:#E9573F; background:rgba(233,87,63,0.15); }
.conduite { color:#FFCE54; background:rgba(255,206,84,0.2); }
.cat { color:#A0826D; background:rgba(160,130,109,0.2); }

.stButton>button {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border-radius: 10px;
    border: none;
    font-weight: 600;
    padding: 0.6rem 1.5rem;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: translateY(-2px);
}

.stSelectbox>div>div,
.stTextArea textarea {
    background: var(--bg-card);
    color: var(--text-main);
    border-radius: 10px;
    border: 1px solid rgba(150,150,150,0.3);
}

label, .stMarkdown {
    color: var(--text-main) !important;
}

::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-thumb {
    background: #667eea;
    border-radius: 10px;
}

/* Mobile-specific styles */
@media (max-width: 768px) {
    .block-container {
        padding: 0.8rem !important;
    }
    
    /* Hide navigation arrows on mobile */
    .stButton>button:contains('◀'),
    .stButton>button:contains('▶') {
        display: none !important;
    }
    
    /* Single column layout on mobile */
    .element-container:has(.note-section) {
        width: 100% !important;
        max-width: 100% !important;
    }
    
    .note-section {
        flex: 1 1 100% !important;
        width: 100% !important;
        max-height: none !important;
        height: auto !important;
        overflow-y: visible !important;
        margin-bottom: 1rem !important;
        padding: 1rem !important;
    }
    
    /* Stack columns vertically on mobile */
    div[data-testid="column"] {
        width: 100% !important;
        min-width: 100% !important;
    }
    
    /* Adjust text input on mobile */
    .stTextArea textarea {
        font-size: 16px !important;
    }
}

/* Tablet adjustments */
@media (min-width: 769px) and (max-width: 1024px) {
    .note-section {
        flex: 0 0 calc(50% - 0.5rem) !important;
    }
}
</style>
"""