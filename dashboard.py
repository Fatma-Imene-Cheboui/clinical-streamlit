"""
Dashboard for visualizing audio recording activity per doctor.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from utils import get_supabase_client


# ─────────────────────────────────────────────
# Data fetching
# ─────────────────────────────────────────────

@st.cache_data(ttl=30)
def fetch_all_activity():
    """Pull every row from clinical_activity."""
    supabase = get_supabase_client()
    res = (
        supabase.table("clinical_activity")
        .select("doctor_username, patient_id, audio_path, notes_path, created_at, updated_at")
        .execute()
    )
    return res.data or []


@st.cache_data(ttl=30)
def fetch_total_patients_per_doctor(df_full: pd.DataFrame):
    """Count total assigned patients per doctor from the main CSV."""
    from data_handler import load_data
    main_df = load_data()
    if "assigned_doctor" not in main_df.columns:
        return {}
    return main_df.groupby("assigned_doctor")["patientId"].nunique().to_dict()


# ─────────────────────────────────────────────
# Styles
# ─────────────────────────────────────────────

DASHBOARD_STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&family=DM+Sans:wght@400;500;600&display=swap');

:root {
    --bg: #0a0c10;
    --surface: #13161d;
    --surface2: #1c202b;
    --border: rgba(255,255,255,0.07);
    --accent: #00e5a0;
    --accent2: #7c6af7;
    --accent3: #f7936a;
    --text: #e8eaf0;
    --muted: #5a6075;
    --danger: #f7476a;
    --warn: #f7c86a;
}

* { font-family: 'DM Sans', sans-serif; box-sizing: border-box; }

.dash-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2rem;
    color: var(--text);
    margin: 0 0 0.2rem 0;
    letter-spacing: -0.03em;
}

.dash-subtitle {
    color: var(--muted);
    font-size: 0.85rem;
    margin: 0 0 2rem 0;
    font-family: 'DM Mono', monospace;
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
}

.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    position: relative;
    overflow: hidden;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.metric-card.green::before  { background: var(--accent); }
.metric-card.purple::before { background: var(--accent2); }
.metric-card.orange::before { background: var(--accent3); }
.metric-card.red::before    { background: var(--danger); }

.metric-label {
    font-size: 0.72rem;
    color: var(--muted);
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    color: var(--text);
    line-height: 1;
}

.metric-value.green  { color: var(--accent); }
.metric-value.purple { color: var(--accent2); }
.metric-value.orange { color: var(--accent3); }
.metric-value.red    { color: var(--danger); }

.metric-sub {
    font-size: 0.75rem;
    color: var(--muted);
    margin-top: 0.3rem;
}

.section-title {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    color: var(--text);
    letter-spacing: -0.01em;
    margin: 1.5rem 0 1rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

.stButton > button {
    background: var(--surface) !important;
    color: var(--accent) !important;
    border: 1px solid rgba(0,229,160,0.3) !important;
    border-radius: 8px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.78rem !important;
    padding: 0.4rem 1rem !important;
    transition: all 0.2s !important;
}

.stButton > button:hover {
    background: rgba(0,229,160,0.08) !important;
    border-color: var(--accent) !important;
    transform: none !important;
}

[data-testid="stAppViewContainer"] > .main {
    background: var(--bg) !important;
}

.block-container { background: var(--bg) !important; }

</style>
"""

AVATAR_COLORS = [
    "#00e5a0", "#7c6af7", "#f7936a", "#f7c86a",
    "#f7476a", "#6af7e5", "#a0f76a", "#f76af2",
    "#6aaff7", "#f76a7c",
]


def _initials(name: str) -> str:
    parts = name.replace("Dr.", "").replace("Dr ", "").strip().split()
    return "".join(p[0].upper() for p in parts[:2]) or "?"


def _badge(pct: float) -> str:
    if pct >= 90:
        return '<span class="badge badge-done">TERMINÉ</span>'
    elif pct >= 40:
        return '<span class="badge badge-mid">EN COURS</span>'
    else:
        return '<span class="badge badge-low">EN ATTENTE</span>'


def _bar_color(pct: float) -> str:
    if pct >= 90:
        return "#00e5a0"
    elif pct >= 40:
        return "#f7c86a"
    return "#f7476a"


# ─────────────────────────────────────────────
# Main render
# ─────────────────────────────────────────────

def render_dashboard():
    st.markdown(DASHBOARD_STYLES, unsafe_allow_html=True)

    # Header
    now_str = datetime.now().strftime("%d %b %Y · %H:%M")
    col_h, col_btn = st.columns([6, 1])
    with col_h:
        st.markdown(
            f'<p class="dash-title">📊 Tableau de bord</p>'
            f'<p class="dash-subtitle">DERNIÈRE MISE À JOUR · {now_str}</p>',
            unsafe_allow_html=True,
        )
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("↻ Actualiser"):
            fetch_all_activity.clear()
            st.rerun()

    # ── Load data ──
    raw = fetch_all_activity()
    if not raw:
        st.info("Aucune activité enregistrée pour le moment.")
        return

    df = pd.DataFrame(raw)
    df["has_audio"] = df["audio_path"].apply(lambda x: bool(x and str(x).strip()))

    # Total patients per doctor from main CSV
    total_map = fetch_total_patients_per_doctor(df)

    # Per-doctor aggregates from activity table
    grp_activity = (
        df.groupby("doctor_username")
        .agg(
            audio_done=("has_audio", "sum"),
        )
        .reset_index()
    )

    # Build full doctor list so 0-activity doctors appear too
    all_doctors = pd.DataFrame({"doctor_username": list(total_map.keys())})
    grp = all_doctors.merge(grp_activity, on="doctor_username", how="left")
    grp["audio_done"] = grp["audio_done"].fillna(0).astype(int)
    grp["total"] = grp["doctor_username"].map(total_map).fillna(0).astype(int)

    # ── Hardcoded overrides ──
    TOTAL_OVERRIDES = {
        "Dr. EL MESSRI":  (60,   60),
        "Dr. Abdelouhab": (60,   60),
        "Dr. Himeur":     (None, 60),
        "Dr. Kadri":      (None, 60),
    }
    for doc, (audio_override, total_override) in TOTAL_OVERRIDES.items():
        mask = grp["doctor_username"] == doc
        if total_override is not None:
            grp.loc[mask, "total"] = total_override
        if audio_override is not None:
            grp.loc[mask, "audio_done"] = audio_override

    grp["pct"] = (grp["audio_done"] / grp["total"].replace(0, 1) * 100).clip(0, 100)
    grp = grp.sort_values("pct", ascending=False).reset_index(drop=True)

    # ── Summary metrics ──
    total_docs = len(grp)
    total_audios = int(df["has_audio"].sum())
    total_patients = int(grp["total"].sum())
    overall_pct = round(total_audios / total_patients * 100, 1) if total_patients else 0

    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card green">
            <div class="metric-label">Audios enregistrés</div>
            <div class="metric-value green">{total_audios}</div>
            <div class="metric-sub">par tous les médecins</div>
        </div>
        <div class="metric-card purple">
            <div class="metric-label">Total patients</div>
            <div class="metric-value purple">{total_patients}</div>
            <div class="metric-sub">assignés dans le système</div>
        </div>
        <div class="metric-card orange">
            <div class="metric-label">Médecins actifs</div>
            <div class="metric-value orange">{total_docs}</div>
            <div class="metric-sub">avec activité enregistrée</div>
        </div>
        <div class="metric-card {'green' if overall_pct >= 75 else 'red'}">
            <div class="metric-label">Complétion globale</div>
            <div class="metric-value {'green' if overall_pct >= 75 else 'red'}">{overall_pct}%</div>
            <div class="metric-sub">audio enregistré</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Per-doctor progress — grouped card grid ──
    def _doctor_card(row):
        initials = _initials(row["doctor_username"])
        pct = float(row["pct"])
        audio = int(row["audio_done"])
        total = int(row["total"])
        name = row["doctor_username"].replace("Dr. ", "").replace("Dr.", "").strip()

        if pct >= 100:
            av_bg, av_color, ring_color = "#0a2e1e", "#00e5a0", "#00e5a0"
            sub = f'<span style="color:#00e5a0;font-weight:600;">{audio} / {total}</span>'
        elif pct > 0:
            av_bg, av_color, ring_color = "#2a1f08", "#f7c86a", "#f7c86a"
            sub = f'<span style="color:#f7c86a;font-weight:600;">{audio} / {total} &middot; {pct:.0f}%</span>'
        else:
            av_bg, av_color, ring_color = "#1c202b", "#5a6075", "#2a2f3d"
            sub = '<span style="color:#5a6075;">0%</span>'

        return f"""
        <div style="background:#13161d;border:1px solid rgba(255,255,255,0.07);border-radius:14px;
                    padding:1.1rem 0.8rem;display:flex;flex-direction:column;align-items:center;gap:8px;">
          <div style="position:relative;width:52px;height:52px;">
            <div style="position:absolute;inset:-4px;border-radius:50%;border:2.5px solid {ring_color};"></div>
            <div style="width:52px;height:52px;border-radius:50%;background:{av_bg};color:{av_color};
                        display:flex;align-items:center;justify-content:center;
                        font-family:'DM Mono',monospace;font-size:12px;font-weight:500;">{initials}</div>
          </div>
          <div style="font-size:12px;font-weight:600;color:#e8eaf0;text-align:center;line-height:1.3;">{name}</div>
          <div style="font-size:11px;font-family:'DM Mono',monospace;">{sub}</div>
        </div>"""

    done_rows = grp[grp["pct"] >= 100]
    prog_rows = grp[(grp["pct"] > 0) & (grp["pct"] < 100)]
    none_rows = grp[grp["pct"] == 0]

    import streamlit.components.v1 as components_prog

    def _render_group(label, rows, accent):
        if rows.empty:
            return
        cards_html = "".join(_doctor_card(r) for _, r in rows.iterrows())
        st.markdown(
            f'<p style="font-size:11px;font-weight:500;color:{accent};letter-spacing:0.08em;'
            f'text-transform:uppercase;margin:1.5rem 0 0.6rem 0;">{label} ({len(rows)})</p>',
            unsafe_allow_html=True
        )
        n = len(rows)
        cols = min(n, 6)
        height = 160 if n <= cols else 320
        components_prog.html(
            f"""<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
            <div style="display:grid;grid-template-columns:repeat({cols},1fr);gap:10px;background:transparent;">{cards_html}</div>""",
            height=height, scrolling=False
        )

    st.markdown('<div class="section-title">Progression par médecin</div>', unsafe_allow_html=True)
    _render_group("Terminé", done_rows, "#00e5a0")
    _render_group("En cours", prog_rows, "#f7c86a")
    _render_group("Non commencé", none_rows, "#5a6075")

    # ── Recent activity table ──
    st.markdown('<div class="section-title">Activité récente</div>', unsafe_allow_html=True)

    recent = df.copy()
    if "updated_at" in recent.columns:
        recent["updated_at"] = pd.to_datetime(recent["updated_at"], errors="coerce")
        recent = recent.sort_values("updated_at", ascending=False).head(20)
    else:
        recent = recent.head(20)

    rows_t = ""
    for _, r in recent.iterrows():
        ts = r.get("updated_at", "")
        ts_str = ts.strftime("%d %b %H:%M") if hasattr(ts, "strftime") else str(ts)[:16]

        if r["has_audio"]:
            status = '<span class="dot dot-audio"></span> Audio'
        else:
            status = '<span class="dot dot-none"></span> Aucun audio'

        rows_t += f"""
        <tr>
            <td class="mono muted">{ts_str}</td>
            <td>{r['doctor_username']}</td>
            <td class="mono">Patient {r['patient_id']}</td>
            <td>{status}</td>
        </tr>
        """

    import streamlit.components.v1 as components
    n_rows = len(recent)
    table_height = 56 + (n_rows * 45) + 20

    components.html(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600&display=swap');
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ background: transparent; }}
        .wrap {{
            background: #13161d;
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 12px;
            overflow: hidden;
            font-family: 'DM Sans', sans-serif;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.83rem;
        }}
        thead tr {{
            background: #1c202b;
            border-bottom: 1px solid rgba(255,255,255,0.07);
        }}
        th {{
            font-family: 'DM Mono', monospace;
            font-size: 0.65rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #5a6075;
            padding: 0.75rem 1.1rem;
            text-align: left;
            font-weight: 500;
        }}
        td {{
            padding: 0.7rem 1.1rem;
            color: #e8eaf0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}
        tr:last-child td {{ border-bottom: none; }}
        tr:hover td {{ background: rgba(255,255,255,0.025); }}
        .mono {{ font-family: 'DM Mono', monospace; }}
        .muted {{ color: #5a6075; }}
        .dot {{
            display: inline-block;
            width: 7px; height: 7px;
            border-radius: 50%;
            margin-right: 5px;
            vertical-align: middle;
            position: relative;
            top: -1px;
        }}
        .dot-audio {{ background: #00e5a0; }}
        .dot-none  {{ background: #5a6075; }}
    </style>
    <div class="wrap">
        <table>
            <thead>
                <tr>
                    <th>Heure</th>
                    <th>Médecin</th>
                    <th>Patient</th>
                    <th>Statut</th>
                </tr>
            </thead>
            <tbody>
                {rows_t}
            </tbody>
        </table>
    </div>
    """, height=table_height, scrolling=False)