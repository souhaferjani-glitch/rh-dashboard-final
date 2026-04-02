import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import warnings
import base64
import os

warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="RH Dashboard - La Pratique Electronique",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== FONCTION POUR CHARGER LE LOGO EN BASE64 ====================
def get_logo_base64():
    logo_paths = ["logo.png", "logo.png", "assets/logo.png", "images/logo.png"]
    for path in logo_paths:
        if os.path.exists(path):
            with open(path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
    return None

LOGO_BASE64 = get_logo_base64()

# ==================== SESSION STATE POUR LE THÈME ====================
if "theme" not in st.session_state:
    st.session_state.theme = "clair"

# ==================== STYLE CSS DYNAMIQUE ====================
def get_theme_css():
    if st.session_state.theme == "clair":
        return """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
            
            * {
                font-family: 'Inter', sans-serif;
            }
            
            .stApp {
                background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
            }
            
            .main-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2rem;
                border-radius: 1rem;
                color: white;
                text-align: center;
                margin-bottom: 2rem;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                animation: fadeIn 0.5s ease-in;
            }
            
            .metric-card {
                background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
                padding: 1.5rem;
                border-radius: 1rem;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                transition: all 0.3s ease;
                border: 1px solid rgba(102, 126, 234, 0.1);
            }
            
            .metric-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
            }
            
            .metric-value {
                font-size: 2.5rem;
                font-weight: 800;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .metric-label {
                font-size: 0.9rem;
                color: #6c757d;
                margin-top: 0.5rem;
                font-weight: 500;
            }
            
            .alert-critical {
                background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%);
                border-left: 4px solid #dc3545;
                padding: 1rem;
                margin: 1rem 0;
                border-radius: 0.5rem;
                color: white;
                font-weight: 500;
                animation: pulse 2s infinite;
            }
            
            .alert-warning {
                background: linear-gradient(135deg, #ffd93d 0%, #ffc107 100%);
                border-left: 4px solid #ffc107;
                padding: 1rem;
                margin: 1rem 0;
                border-radius: 0.5rem;
                color: #333;
                font-weight: 500;
            }
            
            .success-card {
                background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
                border-left: 4px solid #28a745;
                padding: 1rem;
                margin: 1rem 0;
                border-radius: 0.5rem;
                color: white;
                font-weight: 500;
            }
            
            .trend-up {
                color: #51cf66;
                font-weight: bold;
            }
            
            .trend-down {
                color: #ff6b6b;
                font-weight: bold;
            }
            
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
                border-right: 1px solid rgba(102, 126, 234, 0.1);
            }
            
            .stButton > button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 0.5rem;
                transition: all 0.3s ease;
            }
            
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
        </style>
        """
    else:
        return """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
            
            * {
                font-family: 'Inter', sans-serif;
            }
            
            .stApp {
                background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            }
            
            .main-header {
                background: linear-gradient(135deg, #00ffff 0%, #ff00ff 100%);
                padding: 2rem;
                border-radius: 1rem;
                color: white;
                text-align: center;
                margin-bottom: 2rem;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                animation: fadeIn 0.5s ease-in;
            }
            
            .metric-card {
                background: rgba(255,255,255,0.05);
                backdrop-filter: blur(10px);
                padding: 1.5rem;
                border-radius: 1rem;
                text-align: center;
                border: 1px solid rgba(0, 255, 255, 0.2);
                transition: all 0.3s ease;
            }
            
            .metric-card:hover {
                transform: translateY(-5px);
                border-color: rgba(0, 255, 255, 0.5);
                box-shadow: 0 0 30px rgba(0, 255, 255, 0.1);
            }
            
            .metric-value {
                font-size: 2.5rem;
                font-weight: 800;
                background: linear-gradient(135deg, #00ffff, #ff00ff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            .metric-label {
                font-size: 0.9rem;
                color: rgba(255,255,255,0.7);
                margin-top: 0.5rem;
                font-weight: 500;
            }
            
            .alert-critical {
                background: rgba(255,0,0,0.2);
                border-left: 4px solid #ff00ff;
                padding: 1rem;
                margin: 1rem 0;
                border-radius: 0.5rem;
                color: #ff6b6b;
                backdrop-filter: blur(5px);
            }
            
            .alert-warning {
                background: rgba(255,255,0,0.1);
                border-left: 4px solid #00ffff;
                padding: 1rem;
                margin: 1rem 0;
                border-radius: 0.5rem;
                color: #ffd93d;
                backdrop-filter: blur(5px);
            }
            
            .success-card {
                background: rgba(0,255,0,0.1);
                border-left: 4px solid #00ff00;
                padding: 1rem;
                margin: 1rem 0;
                border-radius: 0.5rem;
                color: #51cf66;
                backdrop-filter: blur(5px);
            }
            
            .trend-up {
                color: #00ff00;
                font-weight: bold;
            }
            
            .trend-down {
                color: #ff4444;
                font-weight: bold;
            }
            
            [data-testid="stSidebar"] {
                background: rgba(0,0,0,0.3);
                backdrop-filter: blur(10px);
                border-right: 1px solid rgba(0, 255, 255, 0.2);
            }
            
            [data-testid="stSidebar"] * {
                color: rgba(255,255,255,0.9) !important;
            }
            
            .stButton > button {
                background: linear-gradient(135deg, #00ffff, #ff00ff);
                color: white;
                border: none;
                border-radius: 0.5rem;
                transition: all 0.3s ease;
            }
            
            .stButton > button:hover {
                transform: scale(1.02);
                box-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
            }
            
            .stTextInput > div > div > input {
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(0, 255, 255, 0.3);
                color: white;
            }
        </style>
        """

# ==================== LOGIN ====================
USERS = {"Rhadmin": "admin123"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

def show_login():
    # Logo HTML
    if LOGO_BASE64:
        logo_html = f'<img src="data:image/png;base64,{LOGO_BASE64}" class="logo-large">'
    else:
        logo_html = '<div style="width:120px;height:120px;background:rgba(255,255,255,0.2);border-radius:50%;display:inline-flex;align-items:center;justify-content:center;margin-bottom:24px;border:4px solid rgba(255,255,255,0.3)"><span style="font-size:55px;color:white">📊</span></div>'
    
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {{
        font-family: 'Inter', sans-serif;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}
    
    @keyframes gradientBG {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    
    .stApp {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-size: 200% 200%;
        animation: gradientBG 8s ease infinite;
    }}
    
    .login-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        padding: 40px;
    }}
    
    .login-split-card {{
        display: flex;
        max-width: 900px;
        width: 100%;
        background: white;
        border-radius: 32px;
        overflow: hidden;
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.3);
    }}
    
    .login-left {{
        flex: 1;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 48px 32px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
    }}
    
    .logo-large {{
        width: 120px;
        height: 120px;
        border-radius: 50%;
        object-fit: cover;
        margin-bottom: 24px;
        border: 4px solid rgba(255,255,255,0.3);
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
    }}
    
    .brand-title {{
        font-size: 28px;
        font-weight: 800;
        color: white;
        margin-bottom: 8px;
    }}
    
    .brand-subtitle {{
        font-size: 14px;
        color: rgba(255,255,255,0.8);
        margin-bottom: 16px;
    }}
    
    .login-right {{
        flex: 1;
        padding: 48px 40px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }}
    
    .welcome-title {{
        font-size: 28px;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 32px;
        text-align: center;
    }}
    
    .stButton > button {{
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        font-size: 14px;
        font-weight: 600;
        border-radius: 40px;
        cursor: pointer;
    }}
    
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    </style>
    
    <div class="login-container">
        <div class="login-split-card">
            <div class="login-left">
                {logo_html}
                <div class="brand-title">RH Dashboard</div>
                <div class="brand-subtitle">La Pratique Electronique</div>
            </div>
            <div class="login-right">
                <div class="welcome-title">Bienvenue</div>
    """, unsafe_allow_html=True)
    
    username = st.text_input("", placeholder="Rhadmin", key="login_username", label_visibility="collapsed")
    password = st.text_input("", placeholder="••••••••", type="password", key="login_password", label_visibility="collapsed")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Login", use_container_width=True):
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
    
    st.markdown("""
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

if not st.session_state.logged_in:
    show_login()
    st.stop()

# ==================== APPLIQUER LE THÈME ====================
st.markdown(get_theme_css(), unsafe_allow_html=True)

# ==================== DONNÉES ====================
@st.cache_data
def load_data():
    effectifs = pd.DataFrame({
        'Matricule': ['EMP001','EMP002','EMP003','EMP004','EMP005','EMP006','EMP007','EMP008','EMP009','EMP010','EMP011','EMP012','EMP013','EMP014','EMP015'],
        'Date_Embauche': ['2020-01-01','2021-06-15','2022-03-10','2023-09-05','2021-01-20','2023-07-01','2022-11-15','2020-05-10','2024-02-01','2021-08-15','2023-03-20','2022-12-05','2021-07-10','2023-09-01','2022-04-15'],
        'Date_Sortie': ['','2024-12-01','','','2024-10-15','','2025-03-31','','','','2025-02-28','','','','2025-01-15'],
        'Motif_Sortie': ['','Démission','','','Retraite','','Démission','','','','Licenciement','','','','Démission'],
        'Service': ['Commercial','RH','Technique','Commercial','Administration','Technique','Commercial','RH','Technique','Administration','Commercial','Technique','RH','Commercial','Technique'],
        'Categorie': ['Cadre','Non cadre','Cadre','Non cadre','Cadre','Non cadre','Cadre','Cadre','Non cadre','Non cadre','Non cadre','Cadre','Non cadre','Cadre','Non cadre'],
        'Sexe': ['H','F','H','F','H','F','F','F','H','F','H','H','F','H','F']
    })
    effectifs['Date_Embauche'] = pd.to_datetime(effectifs['Date_Embauche'])
    effectifs['Date_Sortie'] = pd.to_datetime(effectifs['Date_Sortie'], errors='coerce')
    
    mouvements = pd.DataFrame({
        'Mois': ['2024-01-01','2024-02-01','2024-03-01','2024-04-01','2024-05-01','2024-06-01'],
        'Entrees': [2,1,3,0,2,1],
        'Sorties_Dem': [1,0,2,1,0,2],
        'Sorties_Retr': [0,1,0,0,0,0],
        'Sorties_Lice': [0,0,1,0,0,0]
    })
    mouvements['Mois'] = pd.to_datetime(mouvements['Mois'])
    
    promotions = pd.DataFrame({
        'Matricule': ['EMP001','EMP003','EMP008','EMP012'],
        'Date_Promot': ['2025-01-01','2024-03-15','2024-12-01','2024-06-10'],
        'Ancien_Grade': ['Commercial Senior','Technicien','Assistant RH','Ingénieur'],
        'Nouveau_Grade': ['Directeur Commercial','Technicien Principal','Responsable RH','Ingénieur Principal']
    })
    promotions['Date_Promot'] = pd.to_datetime(promotions['Date_Promot'])
    
    questionnaires = pd.DataFrame({
        'Periode': ['01/2024','02/2024','03/2024','04/2024','05/2024','06/2024'],
        'Nb_Diffuses': [50,50,50,50,50,50],
        'Nb_Reponses': [42,38,45,40,44,39],
        'Taux_Reponse': [84,76,90,80,88,78]
    })
    
    entretiens = pd.DataFrame({
        'Annee': [2023,2024,2025],
        'Nb_Planifies': [20,22,15],
        'Nb_Realises': [18,19,13],
        'Taux_Realisation': [90,86.4,86.7]
    })
    
    sanctions = pd.DataFrame({
        'Date': ['2024-01-15','2024-02-20','2024-03-10','2024-04-05','2024-05-12'],
        'Service': ['Commercial','Technique','RH','Commercial','Technique'],
        'Type': ['Avertissement','Blâme','Avertissement','Mise à pied','Blâme']
    })
    sanctions['Date'] = pd.to_datetime(sanctions['Date'])
    
    absenteisme = pd.DataFrame({
        'Mois': ['01/2024','02/2024','03/2024','04/2024','05/2024','06/2024'],
        'Service': ['Commercial','Technique','RH','Commercial','Technique','RH'],
        'Taux_Absence': [5.2,6.8,3.5,6.1,7.2,4.2]
    })
    
    contrats_expiration = pd.DataFrame({
        'Matricule': ['EMP004', 'EMP009', 'EMP014'],
        'Date_Fin': pd.to_datetime(['2026-04-15', '2026-04-20', '2026-05-01']),
        'Type': ['CDD', 'CDD', 'CDD'],
        'Service': ['Commercial', 'Technique', 'Commercial']
    })
    
    return effectifs, mouvements, promotions, questionnaires, entretiens, sanctions, absenteisme, contrats_expiration

effectifs, mouvements, promotions, questionnaires, entretiens, sanctions, absenteisme, contrats_expiration = load_data()

# ==================== CALCULS ====================
actifs = effectifs[effectifs['Date_Sortie'].isna()]
total = len(actifs)
departs = len(effectifs[~effectifs['Date_Sortie'].isna()])
turnover = (departs / len(effectifs) * 100) if len(effectifs) > 0 else 0

cadres = effectifs[effectifs['Categorie'] == 'Cadre']
departs_cadres = len(cadres[~cadres['Date_Sortie'].isna()])
fuite_cadres = (departs_cadres / len(cadres) * 100) if len(cadres) > 0 else 0

recents = effectifs[effectifs['Date_Embauche'] > datetime.now() - timedelta(days=365)]
qualite = (len(recents[recents['Date_Sortie'].isna()]) / len(recents) * 100) if len(recents) > 0 else 0

mouvements['Total_Sorties'] = mouvements['Sorties_Dem'] + mouvements['Sorties_Retr'] + mouvements['Sorties_Lice']

embauches_an_dernier = effectifs[effectifs['Date_Embauche'] > datetime.now() - timedelta(days=365)]
departs_1ere_annee = len(embauches_an_dernier[~embauches_an_dernier['Date_Sortie'].isna()])
taux_depart_1ere = (departs_1ere_annee / len(embauches_an_dernier) * 100) if len(embauches_an_dernier) > 0 else 0

if len(promotions) > 0:
    promo_with_embauche = promotions.merge(effectifs[['Matricule', 'Date_Embauche']], left_on='Matricule', right_on='Matricule')
    promo_with_embauche['Delai'] = (promo_with_embauche['Date_Promot'] - promo_with_embauche['Date_Embauche']).dt.days / 365.25
    delai_promotion = promo_with_embauche['Delai'].mean()
else:
    delai_promotion = 0

services_risque = []
for service in actifs['Service'].unique():
    effectif_service = len(actifs[actifs['Service'] == service])
    departs_service = len(effectifs[(effectifs['Service'] == service) & (~effectifs['Date_Sortie'].isna())])
    turnover_service = (departs_service / effectif_service * 100) if effectif_service > 0 else 0
    
    sanctions_service = len(sanctions[sanctions['Service'] == service])
    taux_sanctions = (sanctions_service / effectif_service * 100) if effectif_service > 0 else 0
    
    absences = absenteisme[absenteisme['Service'] == service]['Taux_Absence'].mean() if service in absenteisme['Service'].values else 0
    
    score_risque = (turnover_service * 0.4) + (taux_sanctions * 0.3) + (absences * 0.3)
    niveau = "🟢 Faible" if score_risque < 10 else "🟡 Moyen" if score_risque < 20 else "🔴 Élevé"
    services_risque.append({'Service': service, 'Score Risque': round(score_risque, 1), 'Niveau': niveau})

date_limite = datetime.now() + timedelta(days=30)
contrats_alertes = contrats_expiration[contrats_expiration['Date_Fin'] <= date_limite]

# ==================== SIDEBAR ====================
with st.sidebar:
    # Logo dans sidebar
    if LOGO_BASE64:
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="data:image/png;base64,{LOGO_BASE64}" style="width: 80px; height: 80px; border-radius: 50%; margin-bottom: 10px; border: 3px solid #667eea;">
            <h3 style="color: #667eea; margin: 0;">La Pratique Electronique</h3>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 50%; margin: 0 auto 10px; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 2rem;">📊</span>
            </div>
            <h3 style="color: #667eea; margin: 0;">La Pratique Electronique</h3>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Bouton changement thème
    theme_col1, theme_col2 = st.columns(2)
    with theme_col1:
        if st.button("☀️ Clair", use_container_width=True):
            st.session_state.theme = "clair"
            st.rerun()
    with theme_col2:
        if st.button("🌙 Sombre", use_container_width=True):
            st.session_state.theme = "sombre"
            st.rerun()
    
    st.markdown("---")
    st.markdown(f"**👤 {st.session_state.username}**")
    st.markdown("---")
    
    service_filter = st.multiselect("Service", actifs['Service'].unique(), default=actifs['Service'].unique())
    categorie_filter = st.multiselect("Catégorie", actifs['Categorie'].unique(), default=actifs['Categorie'].unique())
    sexe_filter = st.multiselect("Sexe", actifs['Sexe'].unique(), default=actifs['Sexe'].unique())
    
    page = st.radio("Navigation", ["🏠 Accueil", "📈 Mouvements", "⭐ Talents", "📋 Admin", "🎯 KPIs", "⚠️ Alertes"])
    
    st.markdown("---")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
    
    st.markdown("---")
    st.caption("© 2025 - La Pratique Electronique")
    st.caption("Version 2.0 - Business Intelligence")

# ==================== PAGE ACCUEIL ====================
if page == "🏠 Accueil":
    st.markdown(f'<div class="main-header"><h1>📊 Tableau de Bord RH</h1><p> - La Pratique Electronique - </p></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total}</div><div class="metric-label">👥 Effectif Total</div><div class="trend-up">+{total-15} cette année</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{turnover:.1f}%</div><div class="metric-label">📈 Taux de Rotation</div><div class="trend-down">Objectif: <15%</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(promotions)}</div><div class="metric-label">⭐ Promotions</div><div class="trend-up">+33% vs 2023</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{departs}</div><div class="metric-label">🚪 Départs</div><div class="trend-down">-2 vs 2023</div></div>', unsafe_allow_html=True)
    
    effectifs_filtres = actifs[actifs['Service'].isin(service_filter) & actifs['Categorie'].isin(categorie_filter) & actifs['Sexe'].isin(sexe_filter)]
    effectifs_service = effectifs_filtres.groupby('Service').size().reset_index(name='Effectif')
    fig = px.pie(effectifs_service, values='Effectif', names='Service', title="🏢 Répartition par Service", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("📊 Indicateurs Complémentaires")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Cadres", len(cadres), delta=f"{len(cadres)/total*100:.0f}%")
    with col2:
        st.metric("👩 Femmes", len(actifs[actifs['Sexe']=='F']), delta=f"{len(actifs[actifs['Sexe']=='F'])/total*100:.0f}%")
    with col3:
        st.metric("👨 Hommes", len(actifs[actifs['Sexe']=='H']), delta=f"{len(actifs[actifs['Sexe']=='H'])/total*100:.0f}%")
    with col4:
        st.metric("📊 Taux réponse", f"{questionnaires['Taux_Reponse'].mean():.0f}%")

# ==================== PAGE MOUVEMENTS ====================
elif page == "📈 Mouvements":
    st.markdown('<div class="main-header"><h1>📈 Mouvements du Personnel</h1><p>Entrées, sorties et turnover</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📥 Total Entrées", mouvements['Entrees'].sum())
    with col2:
        st.metric("📤 Total Sorties", mouvements['Total_Sorties'].sum())
    with col3:
        st.metric("⚖️ Solde Net", mouvements['Entrees'].sum() - mouvements['Total_Sorties'].sum())
    with col4:
        st.metric("🔄 Turnover", f"{turnover:.1f}%")
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=mouvements['Mois'].dt.strftime('%b %Y'), y=mouvements['Entrees'], name='Entrées', marker_color='#51cf66', text=mouvements['Entrees'], textposition='outside'))
    fig.add_trace(go.Bar(x=mouvements['Mois'].dt.strftime('%b %Y'), y=mouvements['Total_Sorties'], name='Sorties', marker_color='#ff6b6b', text=mouvements['Total_Sorties'], textposition='outside'))
    fig.update_layout(title='Entrées vs Sorties mensuelles', barmode='group', height=450)
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📊 Motifs de Sortie")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📝 Démission", mouvements['Sorties_Dem'].sum())
    with col2:
        st.metric("👴 Retraite", mouvements['Sorties_Retr'].sum())
    with col3:
        st.metric("⚖️ Licenciement", mouvements['Sorties_Lice'].sum())
    
    st.subheader("📊 Taux de départ durant la première année")
    if len(embauches_an_dernier) > 0:
        st.metric("Taux", f"{taux_depart_1ere:.1f}%", delta="Objectif <20%")
        st.progress(taux_depart_1ere/100)

# ==================== PAGE TALENTS ====================
elif page == "⭐ Talents":
    st.markdown('<div class="main-header"><h1>⭐ Gestion des Talents</h1><p>Promotions et mobilité interne</p></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📋 Historique des promotions")
        st.dataframe(promotions, use_container_width=True)
        st.metric("📊 Total promotions", len(promotions))
    with col2:
        st.subheader("⏱️ Délai moyen de promotion")
        st.metric("Valeur", f"{delai_promotion:.1f} ans", delta="Objectif <3 ans")
        st.subheader("🔄 Mobilité interne")
        st.metric("Changements", len(promotions))

# ==================== PAGE ADMIN ====================
elif page == "📋 Admin":
    st.markdown('<div class="main-header"><h1>📋 Gestion Administrative</h1><p>Suivi des indicateurs administratifs RH</p></div>', unsafe_allow_html=True)
    
    st.subheader("📊 Taux de réponse aux questionnaires")
    taux_reponse_moyen = questionnaires['Taux_Reponse'].mean()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Taux moyen", f"{taux_reponse_moyen:.1f}%")
    with col2:
        st.metric("Questionnaires diffusés", questionnaires['Nb_Diffuses'].sum())
    with col3:
        st.metric("Réponses reçues", questionnaires['Nb_Reponses'].sum())
    
    st.subheader("📋 Entretiens annuels")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Taux de réalisation", f"{entretiens['Taux_Realisation'].mean():.1f}%")
    with col2:
        st.metric("Planifiés", entretiens['Nb_Planifies'].sum())
    with col3:
        st.metric("Réalisés", entretiens['Nb_Realises'].sum())
    
    st.subheader("⚠️ Contrats arrivant à expiration (30 jours)")
    if len(contrats_alertes) > 0:
        st.error(f"🚨 {len(contrats_alertes)} contrat(s) expire(nt) dans les 30 jours")
        st.dataframe(contrats_alertes, use_container_width=True)
    else:
        st.success("✅ Aucun contrat n'expire dans les 30 jours")
    
    st.subheader("⚖️ Sanctions disciplinaires")
    st.dataframe(sanctions, use_container_width=True)
    
    st.subheader("📊 Taux d'absentéisme par service")
    fig = px.bar(absenteisme, x='Service', y='Taux_Absence', title="Taux d'absentéisme", text='Taux_Absence')
    fig.add_hline(y=8, line_dash="dash", line_color="red", annotation_text="Seuil d'alerte 8%")
    st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE KPIs ====================
elif page == "🎯 KPIs":
    st.markdown('<div class="main-header"><h1>🎯 Indicateurs Stratégiques</h1><p>Performance RH</p></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure(go.Indicator(mode="gauge+number", value=qualite, title="Qualité des recrutements", gauge={'axis': {'range': [0, 100]}}))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = go.Figure(go.Indicator(mode="gauge+number", value=fuite_cadres, title="Fuite des compétences", gauge={'axis': {'range': [0, 30]}}))
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("🎯 Score de risque par service")
    st.dataframe(pd.DataFrame(services_risque), use_container_width=True)

# ==================== PAGE ALERTES ====================
elif page == "⚠️ Alertes":
    st.markdown('<div class="main-header"><h1>⚠️ Système d\'Alertes</h1><p>Détection automatique des risques</p></div>', unsafe_allow_html=True)
    
    if turnover > 15:
        st.error(f"🔴 Turnover élevé: {turnover:.1f}% (Seuil > 15%)")
    if fuite_cadres > 10:
        st.error(f"🔴 Fuite des cadres: {fuite_cadres:.1f}% (Seuil > 10%)")
    elif fuite_cadres > 5:
        st.warning(f"🟡 Fuite des cadres: {fuite_cadres:.1f}% (Seuil > 5%)")
    if qualite < 80:
        st.warning(f"🟡 Qualité recrutements: {qualite:.1f}% (Seuil < 80%)")
    if len(contrats_alertes) > 0:
        st.warning(f"🟡 {len(contrats_alertes)} contrat(s) expire(nt) dans 30 jours")
    
    st.markdown('<div class="success-card">✅ Tous les indicateurs sont surveillés</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption("🎓 La Pratique Electronique | Projet PFE - Souha Ferjani | Business Intelligence")
