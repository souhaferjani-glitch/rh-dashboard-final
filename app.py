import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="HR Analytics Pro",
    page_icon="🎯",
    layout="wide"
)

# ============================================
# STYLE PERSONNALISÉ - DESIGN PROFESSIONNEL
# ============================================
st.markdown("""
<style>
    /* Police moderne */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Couleurs principales */
    :root {
        --primary: #4361ee;
        --secondary: #3f37c9;
        --success: #4caf50;
        --danger: #f44336;
        --warning: #ff9800;
        --dark: #1a1a2e;
        --light: #f8f9fa;
    }
    
    /* Header */
    .hero-header {
        background: linear-gradient(135deg, #4361ee 0%, #3f37c9 100%);
        padding: 2rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 10px 30px rgba(67, 97, 238, 0.2);
    }
    
    /* Cartes KPI */
    .kpi-card {
        background: white;
        border-radius: 16px;
        padding: 1.2rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
        transition: all 0.3s;
    }
    
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(67, 97, 238, 0.1);
        border-color: #4361ee;
    }
    
    .kpi-number {
        font-size: 2rem;
        font-weight: 700;
        color: #4361ee;
        margin: 0;
    }
    
    .kpi-label {
        font-size: 0.75rem;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.5rem;
    }
    
    .kpi-change-up {
        color: #4caf50;
        font-size: 0.7rem;
        font-weight: 500;
    }
    
    .kpi-change-down {
        color: #f44336;
        font-size: 0.7rem;
        font-weight: 500;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stRadio label {
        background: rgba(255,255,255,0.1);
        padding: 8px 12px;
        border-radius: 10px;
        margin: 4px 0;
    }
    
    /* Alertes */
    .alert-box {
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
    }
    
    .alert-critical {
        background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
        color: white;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
        color: white;
    }
    
    .alert-success {
        background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);
        color: white;
    }
    
    /* Login Page */
    .login-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        background: linear-gradient(135deg, #4361ee 0%, #3f37c9 100%);
    }
    
    .login-card {
        background: white;
        padding: 2.5rem;
        border-radius: 24px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        text-align: center;
        width: 100%;
        max-width: 400px;
    }
    
    .login-icon {
        width: 70px;
        height: 70px;
        background: linear-gradient(135deg, #4361ee 0%, #3f37c9 100%);
        border-radius: 18px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1rem;
    }
    
    .login-icon span {
        font-size: 2rem;
    }
    
    /* Boutons */
    .stButton > button {
        background: linear-gradient(135deg, #4361ee 0%, #3f37c9 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    /* Section title */
    .section-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1a1a2e;
        margin: 1rem 0;
        padding-left: 0.5rem;
        border-left: 4px solid #4361ee;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# LOGIN SYSTEM
# ============================================
USERS = {"admin": "admin123"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

def login_page():
    st.markdown("""
    <div class="login-wrapper">
        <div class="login-card">
            <div class="login-icon">
                <span>📊</span>
            </div>
            <h2 style="color: #1a1a2e; margin: 0;">HR Analytics Pro</h2>
            <p style="color: #6c757d; margin-bottom: 1.5rem;">La Pratique Electronique</p>
    """, unsafe_allow_html=True)
    
    username = st.text_input("", placeholder="Nom d'utilisateur", key="login_user")
    password = st.text_input("", placeholder="Mot de passe", type="password", key="login_pass")
    
    if st.button("Se connecter", use_container_width=True):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("❌ Identifiants incorrects")
    
    st.markdown("</div></div>", unsafe_allow_html=True)

if not st.session_state.logged_in:
    login_page()
    st.stop()

# ============================================
# DONNÉES
# ============================================
@st.cache_data
def get_data():
    effectifs = pd.DataFrame({
        'Matricule': [f'EMP{i:03d}' for i in range(1, 21)],
        'Date_Embauche': pd.date_range('2020-01-01', periods=20, freq='ME'),
        'Service': np.random.choice(['Commercial', 'Technique', 'RH', 'Admin'], 20),
        'Categorie': np.random.choice(['Cadre', 'Non-cadre'], 20, p=[0.4, 0.6]),
        'Sexe': np.random.choice(['H', 'F'], 20, p=[0.55, 0.45])
    })
    effectifs['Date_Sortie'] = pd.NA
    effectifs.loc[effectifs.index % 5 == 0, 'Date_Sortie'] = effectifs['Date_Embauche'] + pd.Timedelta(days=np.random.randint(100, 500))
    
    mouvements = pd.DataFrame({
        'Mois': pd.date_range('2024-01-01', periods=6, freq='ME'),
        'Entrees': np.random.randint(1, 5, 6),
        'Sorties': np.random.randint(0, 3, 6)
    })
    
    promotions = pd.DataFrame({
        'Employe': ['EMP001', 'EMP003', 'EMP005', 'EMP008'],
        'Date': pd.to_datetime(['2024-03-15', '2024-06-01', '2024-09-10', '2024-12-01']),
        'Ancien': ['Assistant', 'Technicien', 'Commercial', 'Analyste'],
        'Nouveau': ['Chef Projet', 'Ingénieur', 'Manager', 'Senior']
    })
    
    return effectifs, mouvements, promotions

effectifs, mouvements, promotions = get_data()

# Calculs
actifs = effectifs[effectifs['Date_Sortie'].isna()]
total = len(actifs)
turnover = len(effectifs[~effectifs['Date_Sortie'].isna()]) / len(effectifs) * 100
cadres = len(effectifs[effectifs['Categorie'] == 'Cadre'])
femmes = len(effectifs[effectifs['Sexe'] == 'F'])

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1.5rem;">
        <div style="background: rgba(255,255,255,0.1); width: 60px; height: 60px; border-radius: 15px; margin: 0 auto; display: flex; align-items: center; justify-content: center;">
            <span style="font-size: 1.8rem;">🎯</span>
        </div>
        <h3 style="margin: 0.5rem 0 0 0;">HR Pro</h3>
        <p style="font-size: 0.7rem; opacity: 0.7;">La Pratique Electronique</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"**👤 {st.session_state.username}**")
    st.markdown("---")
    
    menu = st.radio("", ["🏠 Dashboard", "📊 Mouvements", "⭐ Talents", "⚙️ Admin", "🎯 KPIs", "🔔 Alertes"])
    
    st.markdown("---")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    
    st.caption("© 2025 | Souha Ferjani")

# ============================================
# PAGES
# ============================================

# ---------- DASHBOARD ----------
if menu == "🏠 Dashboard":
    st.markdown("""
    <div class="hero-header">
        <h1 style="margin: 0;">Tableau de Bord RH</h1>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Suivi en temps réel des indicateurs clés</p>
    </div>
    """, unsafe_allow_html=True)
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-number">{total}</div>
            <div class="kpi-label">Effectif Total</div>
            <div class="kpi-change-up">▲ +5 cette année</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-number">{turnover:.1f}%</div>
            <div class="kpi-label">Taux Turnover</div>
            <div class="kpi-change-down">▼ Objectif &lt;15%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-number">{cadres}</div>
            <div class="kpi-label">Cadres</div>
            <div class="kpi-change-up">{cadres/total*100:.0f}% des effectifs</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-number">{femmes}</div>
            <div class="kpi-label">Femmes</div>
            <div class="kpi-change-up">{femmes/total*100:.0f}% des effectifs</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        service_counts = actifs['Service'].value_counts().reset_index()
        service_counts.columns = ['Service', 'Effectif']
        fig = px.bar(service_counts, x='Service', y='Effectif', 
                     title="📊 Effectifs par Service", text='Effectif',
                     color='Effectif', color_continuous_scale='Blues')
        fig.update_traces(textposition='outside')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.pie(actifs, names='Categorie', title="👥 Répartition Cadres / Non-cadres",
                     hole=0.4, color_discrete_sequence=['#4361ee', '#a0c4ff'])
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Dernières promotions
    st.markdown('<div class="section-title">⭐ Dernières Promotions</div>', unsafe_allow_html=True)
    st.dataframe(promotions, use_container_width=True)

# ---------- MOUVEMENTS ----------
elif menu == "📊 Mouvements":
    st.markdown("""
    <div class="hero-header">
        <h1>Mouvements du Personnel</h1>
        <p>Analyse des flux entrants et sortants</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📥 Total Entrées", mouvements['Entrees'].sum())
    with col2:
        st.metric("📤 Total Sorties", mouvements['Sorties'].sum())
    with col3:
        st.metric("📊 Solde Net", mouvements['Entrees'].sum() - mouvements['Sorties'].sum())
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=mouvements['Mois'].dt.strftime('%b %Y'), y=mouvements['Entrees'], 
                         name='Entrées', marker_color='#4caf50'))
    fig.add_trace(go.Bar(x=mouvements['Mois'].dt.strftime('%b %Y'), y=mouvements['Sorties'], 
                         name='Sorties', marker_color='#f44336'))
    fig.update_layout(title="Entrées vs Sorties", barmode='group', height=450)
    st.plotly_chart(fig, use_container_width=True)

# ---------- TALENTS ----------
elif menu == "⭐ Talents":
    st.markdown("""
    <div class="hero-header">
        <h1>Gestion des Talents</h1>
        <p>Suivi des promotions et mobilité interne</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("⭐ Total Promotions", len(promotions))
        st.dataframe(promotions, use_container_width=True)
    with col2:
        st.metric("📈 Mobilité Interne", len(promotions))
        st.info("Période: 2024-2025")

# ---------- ADMIN ----------
elif menu == "⚙️ Admin":
    st.markdown("""
    <div class="hero-header">
        <h1>Gestion Administrative</h1>
        <p>Indicateurs administratifs RH</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.success("✅ Module en cours de développement")
    st.info("📋 Taux de réponse questionnaires: 78%")
    st.info("📊 Entretiens annuels: 86% réalisés")

# ---------- KPIs ----------
elif menu == "🎯 KPIs":
    st.markdown("""
    <div class="hero-header">
        <h1>Indicateurs Stratégiques</h1>
        <p>Performance RH et score de risque</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure(go.Indicator(mode="gauge+number", value=78, 
                                     title="Qualité Recrutement",
                                     gauge={'axis': {'range': [0, 100]}}))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = go.Figure(go.Indicator(mode="gauge+number", value=12, 
                                     title="Fuite Cadres",
                                     gauge={'axis': {'range': [0, 30]}}))
        st.plotly_chart(fig, use_container_width=True)

# ---------- ALERTES ----------
elif menu == "🔔 Alertes":
    st.markdown("""
    <div class="hero-header">
        <h1>Système d'Alerte</h1>
        <p>Détection automatique des risques</p>
    </div>
    """, unsafe_allow_html=True)
    
    if turnover > 15:
        st.markdown('<div class="alert-box alert-critical">🔴 ALERTE CRITIQUE: Turnover élevé</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-box alert-success">✅ Turnover sous contrôle</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="alert-box alert-warning">🟡 ATTENTION: Surveiller les départs cadres</div>', unsafe_allow_html=True)
