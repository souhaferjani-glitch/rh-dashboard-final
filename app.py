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
    page_title="RH Vision - Modern Dashboard",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== FONCTION POUR CHARGER LE LOGO ====================
def get_logo_base64():
    logo_paths = ["logo.png", "logo.PNG", "assets/logo.png", "images/logo.png"]
    for path in logo_paths:
        if os.path.exists(path):
            with open(path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
    return None

LOGO_BASE64 = get_logo_base64()

# ==================== STYLE MODERNE ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
    }
    
    .glass-header {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    
    .modern-card {
        background: white;
        border-radius: 1.5rem;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        border: 1px solid #eef2f6;
    }
    
    .modern-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    .kpi-value {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .badge-success {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 0.25rem 1rem;
        border-radius: 2rem;
        color: white;
        font-size: 0.8rem;
        font-weight: 500;
        display: inline-block;
    }
    
    .badge-warning {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        padding: 0.25rem 1rem;
        border-radius: 2rem;
        color: white;
        font-size: 0.8rem;
        font-weight: 500;
        display: inline-block;
    }
    
    .badge-danger {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        padding: 0.25rem 1rem;
        border-radius: 2rem;
        color: white;
        font-size: 0.8rem;
        font-weight: 500;
        display: inline-block;
    }
    
    .alert-modern {
        background: linear-gradient(135deg, #fee2e2 0%, #ffedea 100%);
        border-left: 4px solid #ef4444;
        padding: 1rem;
        border-radius: 1rem;
        margin: 1rem 0;
    }
    
    .stat-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem;
        background: #f8fafc;
        border-radius: 1rem;
        margin: 0.5rem 0;
    }
    
    hr {
        margin: 2rem 0;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
    }
    
    /* Style pour la sidebar avec logo */
    .sidebar-logo {
        text-align: center;
        padding: 1rem 0;
    }
    .sidebar-logo img {
        width: 70px;
        height: 70px;
        border-radius: 1rem;
        object-fit: cover;
        margin-bottom: 0.5rem;
    }
    
    /* Style pour la page configuration */
    .config-section {
        background: white;
        border-radius: 1.5rem;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #eef2f6;
    }
    .config-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SIDEBAR AVEC LOGO ====================
with st.sidebar:
    if LOGO_BASE64:
        st.markdown(f"""
        <div class="sidebar-logo">
            <img src="data:image/png;base64,{LOGO_BASE64}" alt="Logo">
            <h3 style="margin-top: 0.5rem; color: #0f172a;">RH Vision</h3>
            <p style="color: #64748b; font-size: 0.7rem;">La Pratique Electronique</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="sidebar-logo">
            <div style="background: linear-gradient(135deg, #0ea5e9, #6366f1); width: 70px; height: 70px; border-radius: 1rem; margin: 0 auto; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 2rem;">✨</span>
            </div>
            <h3 style="margin-top: 0.5rem; color: #0f172a;">RH Vision</h3>
            <p style="color: #64748b; font-size: 0.7rem;">La Pratique Electronique</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filtres
    st.markdown("### 🎯 Filtres")
    service_filter = st.multiselect("Service", actifs['Service'].unique(), default=actifs['Service'].unique())
    categorie_filter = st.multiselect("Catégorie", actifs['Categorie'].unique(), default=actifs['Categorie'].unique())
    
    st.markdown("---")
    page = st.radio("Navigation", ["📊 Tableau de Bord", "📈 Mouvements", "⭐ Talents", "⚙️ Administration", "🎯 KPIs", "⚠️ Alertes", "⚙️ Configuration"])
    
    st.markdown("---")
    st.caption("© 2025 - RH Vision")
    st.caption("Version 2.0")

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
    niveau = "Faible" if score_risque < 10 else "Moyen" if score_risque < 20 else "Élevé"
    services_risque.append({'Service': service, 'Score Risque': round(score_risque, 1), 'Niveau': niveau})

date_limite = datetime.now() + timedelta(days=30)
contrats_alertes = contrats_expiration[contrats_expiration['Date_Fin'] <= date_limite]

# ==================== PAGE TABLEAU DE BORD ====================
if page == "📊 Tableau de Bord":
    st.markdown("""
    <div class="glass-header">
        <h1 style="margin: 0; background: linear-gradient(135deg, #0ea5e9, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            Tableau de Bord RH
        </h1>
        <p style="color: #64748b; margin-top: 0.5rem;">Suivi en temps réel des indicateurs clés</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="modern-card">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <span style="font-size: 2rem;">👥</span>
                <span class="badge-success">+{total-15}</span>
            </div>
            <div class="kpi-value">{total}</div>
            <div style="color: #64748b; margin-top: 0.5rem;">Effectif Total</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        statut = "badge-success" if turnover < 15 else "badge-warning" if turnover < 20 else "badge-danger"
        st.markdown(f"""
        <div class="modern-card">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <span style="font-size: 2rem;">🔄</span>
                <span class="{statut}">{'✓' if turnover < 15 else '⚠️'}</span>
            </div>
            <div class="kpi-value">{turnover:.1f}%</div>
            <div style="color: #64748b; margin-top: 0.5rem;">Taux de Rotation</div>
            <div style="font-size: 0.75rem; color: #94a3b8;">Objectif: {'✓ Atteint' if turnover < 15 else '&lt;15%'}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="modern-card">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <span style="font-size: 2rem;">⭐</span>
                <span class="badge-success">+33%</span>
            </div>
            <div class="kpi-value">{len(promotions)}</div>
            <div style="color: #64748b; margin-top: 0.5rem;">Promotions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="modern-card">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <span style="font-size: 2rem;">🚪</span>
                <span class="badge-success">-2</span>
            </div>
            <div class="kpi-value">{departs}</div>
            <div style="color: #64748b; margin-top: 0.5rem;">Départs</div>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        effectifs_filtres = actifs[actifs['Service'].isin(service_filter) & actifs['Categorie'].isin(categorie_filter)]
        effectifs_service = effectifs_filtres.groupby('Service').size().reset_index(name='Effectif')
        fig = px.pie(effectifs_service, values='Effectif', names='Service', 
                     title="🏢 Répartition par Service", hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(height=400, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=mouvements['Mois'].dt.strftime('%b %Y'), y=mouvements['Entrees'], 
                             name='Entrées', marker_color='#10b981', text=mouvements['Entrees'], textposition='outside'))
        fig.add_trace(go.Bar(x=mouvements['Mois'].dt.strftime('%b %Y'), y=mouvements['Total_Sorties'], 
                             name='Sorties', marker_color='#ef4444', text=mouvements['Total_Sorties'], textposition='outside'))
        fig.update_layout(title='Entrées vs Sorties mensuelles', barmode='group', height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📊 Indicateurs Complémentaires")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="stat-container">
            <div>👨‍💼 Cadres</div>
            <div><strong>{len(cadres)}</strong> <span style="color: #10b981;">({len(cadres)/total*100:.0f}%)</span></div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-container">
            <div>👩 Femmes</div>
            <div><strong>{len(actifs[actifs['Sexe']=='F'])}</strong> <span style="color: #10b981;">({len(actifs[actifs['Sexe']=='F'])/total*100:.0f}%)</span></div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stat-container">
            <div>👨 Hommes</div>
            <div><strong>{len(actifs[actifs['Sexe']=='H'])}</strong> <span style="color: #10b981;">({len(actifs[actifs['Sexe']=='H'])/total*100:.0f}%)</span></div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="stat-container">
            <div>📊 Taux réponse</div>
            <div><strong>{questionnaires['Taux_Reponse'].mean():.0f}%</strong></div>
        </div>
        """, unsafe_allow_html=True)

# ==================== PAGE MOUVEMENTS ====================
elif page == "📈 Mouvements":
    st.markdown("""
    <div class="glass-header">
        <h1 style="margin: 0;">📈 Mouvements du Personnel</h1>
        <p>Analyse des flux entrants et sortants</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="modern-card">
            <div style="font-size: 2rem;">📥</div>
            <div class="kpi-value">{mouvements['Entrees'].sum()}</div>
            <div>Total Entrées</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="modern-card">
            <div style="font-size: 2rem;">📤</div>
            <div class="kpi-value">{mouvements['Total_Sorties'].sum()}</div>
            <div>Total Sorties</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="modern-card">
            <div style="font-size: 2rem;">⚖️</div>
            <div class="kpi-value">{mouvements['Entrees'].sum() - mouvements['Total_Sorties'].sum()}</div>
            <div>Solde Net</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="modern-card">
            <div style="font-size: 2rem;">🔄</div>
            <div class="kpi-value">{turnover:.1f}%</div>
            <div>Turnover</div>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="modern-card">
            <div>📝 Démission</div>
            <div class="kpi-value">{mouvements['Sorties_Dem'].sum()}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="modern-card">
            <div>👴 Retraite</div>
            <div class="kpi-value">{mouvements['Sorties_Retr'].sum()}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="modern-card">
            <div>⚖️ Licenciement</div>
            <div class="kpi-value">{mouvements['Sorties_Lice'].sum()}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Turnover par Service")
    turnover_service = []
    for service in actifs['Service'].unique():
        effectif_service = len(actifs[actifs['Service'] == service])
        departs_service = len(effectifs[(effectifs['Service'] == service) & (~effectifs['Date_Sortie'].isna())])
        taux = (departs_service / effectif_service * 100) if effectif_service > 0 else 0
        turnover_service.append({'Service': service, 'Turnover (%)': round(taux, 1)})
    st.dataframe(pd.DataFrame(turnover_service), use_container_width=True)
    
    st.markdown("### 📊 Taux de départ durant la première année")
    if len(embauches_an_dernier) > 0:
        st.markdown(f"""
        <div class="modern-card">
            <div class="kpi-value">{taux_depart_1ere:.1f}%</div>
            <div>Objectif: {'✓ Atteint' if taux_depart_1ere < 20 else '&lt;20%'}</div>
            <progress value="{taux_depart_1ere}" max="100" style="width: 100%; height: 8px; border-radius: 4px;"></progress>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("ℹ️ Pas d'embauches dans la dernière année")

# ==================== PAGE TALENTS ====================
elif page == "⭐ Talents":
    st.markdown("""
    <div class="glass-header">
        <h1 style="margin: 0;">⭐ Gestion des Talents</h1>
        <p>Promotions et mobilité interne</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="modern-card">
            <div style="font-size: 2rem;">📋</div>
            <div class="kpi-value">{len(promotions)}</div>
            <div>Total Promotions</div>
        </div>
        """, unsafe_allow_html=True)
        st.dataframe(promotions, use_container_width=True)
    
    with col2:
        st.markdown(f"""
        <div class="modern-card">
            <div style="font-size: 2rem;">⏱️</div>
            <div class="kpi-value">{delai_promotion:.1f}</div>
            <div>Délai moyen de promotion (ans)</div>
            <div style="font-size: 0.75rem;">Objectif: {'✓ Atteint' if delai_promotion < 3 else '&lt;3 ans'}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="modern-card">
            <div style="font-size: 2rem;">🔄</div>
            <div class="kpi-value">{len(promotions)}</div>
            <div>Mobilité interne</div>
            <div style="font-size: 0.75rem;">Période: 2024-2025</div>
        </div>
        """, unsafe_allow_html=True)
    
    if len(promotions) > 0:
        promotions_par_annee = promotions.groupby(promotions['Date_Promot'].dt.year).size().reset_index(name='Nombre')
        promotions_par_annee.columns = ['Année', 'Nombre']
        fig = px.bar(promotions_par_annee, x='Année', y='Nombre', title="Promotions par année", text='Nombre')
        fig.update_traces(marker_color='#6366f1', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE ADMINISTRATION ====================
elif page == "⚙️ Administration":
    st.markdown("""
    <div class="glass-header">
        <h1 style="margin: 0;">⚙️ Gestion Administrative</h1>
        <p>Suivi des indicateurs administratifs RH</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Taux de réponse aux questionnaires")
    taux_reponse_moyen = questionnaires['Taux_Reponse'].mean()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="modern-card">
            <div class="kpi-value">{taux_reponse_moyen:.1f}%</div>
            <div>Taux moyen</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="modern-card">
            <div class="kpi-value">{questionnaires['Nb_Diffuses'].sum()}</div>
            <div>Questionnaires diffusés</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="modern-card">
            <div class="kpi-value">{questionnaires['Nb_Reponses'].sum()}</div>
            <div>Réponses reçues</div>
        </div>
        """, unsafe_allow_html=True)
    
    fig = px.line(questionnaires, x='Periode', y='Taux_Reponse', title="Évolution du taux de participation", markers=True)
    fig.add_hline(y=75, line_dash="dash", line_color="#f59e0b")
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 📋 Entretiens annuels")
    taux_entretien_moyen = entretiens['Taux_Realisation'].mean()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="modern-card">
            <div class="kpi-value">{taux_entretien_moyen:.1f}%</div>
            <div>Taux de réalisation</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="modern-card">
            <div class="kpi-value">{entretiens['Nb_Planifies'].sum()}</div>
            <div>Entretiens planifiés</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="modern-card">
            <div class="kpi-value">{entretiens['Nb_Realises'].sum()}</div>
            <div>Entretiens réalisés</div>
        </div>
        """, unsafe_allow_html=True)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=entretiens['Annee'], y=entretiens['Taux_Realisation'], text=entretiens['Taux_Realisation'], texttemplate='%{text:.1f}%', textposition='outside'))
    fig.add_hline(y=80, line_dash="dash", line_color="#ef4444")
    fig.update_layout(title="Taux de réalisation des entretiens annuels", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### ⚠️ Contrats arrivant à expiration (30 jours)")
    if len(contrats_alertes) > 0:
        st.markdown(f"""
        <div class="alert-modern">
            🚨 {len(contrats_alertes)} contrat(s) expire(nt) dans les 30 jours
        </div>
        """, unsafe_allow_html=True)
        st.dataframe(contrats_alertes, use_container_width=True)
    else:
        st.success("✅ Aucun contrat n'expire dans les 30 jours")
    
    st.markdown("### ⚖️ Sanctions disciplinaires")
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(sanctions, use_container_width=True)
    with col2:
        sanctions_par_service = sanctions.groupby('Service').size().reset_index(name='Nb_Sanctions')
        fig = px.pie(sanctions_par_service, values='Nb_Sanctions', names='Service', title="Sanctions par service", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 📊 Taux d'absentéisme par service")
    fig = px.bar(absenteisme, x='Service', y='Taux_Absence', title="Taux d'absentéisme", text='Taux_Absence')
    fig.add_hline(y=8, line_dash="dash", line_color="#ef4444")
    st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE KPIs ====================
elif page == "🎯 KPIs":
    st.markdown("""
    <div class="glass-header">
        <h1 style="margin: 0;">🎯 Indicateurs Stratégiques</h1>
        <p>Performance RH et score de risque</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure(go.Indicator(mode="gauge+number", value=qualite, title={'text': "Qualité des recrutements"},
                                       gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#10b981"},
                                              'steps': [{'range': [0, 50], 'color': '#fee2e2'}, {'range': [50, 80], 'color': '#fed7aa'}, {'range': [80, 100], 'color': '#d1fae5'}]}))
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = go.Figure(go.Indicator(mode="gauge+number", value=fuite_cadres, title={'text': "Fuite des compétences"},
                                       gauge={'axis': {'range': [0, 30]}, 'bar': {'color': "#ef4444"},
                                              'steps': [{'range': [0, 5], 'color': '#d1fae5'}, {'range': [5, 10], 'color': '#fed7aa'}, {'range': [10, 30], 'color': '#fee2e2'}]}))
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 🎯 Score de risque par service")
    st.dataframe(pd.DataFrame(services_risque), use_container_width=True)
    
    fig = px.bar(pd.DataFrame(services_risque), x='Service', y='Score Risque', 
                 title="Score de risque par service", color='Score Risque',
                 color_continuous_scale=['#10b981', '#f59e0b', '#ef4444'])
    st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE ALERTES ====================
elif page == "⚠️ Alertes":
    st.markdown("""
    <div class="glass-header">
        <h1 style="margin: 0;">⚠️ Système d'Alerte</h1>
        <p>Détection automatique des risques RH</p>
    </div>
    """, unsafe_allow_html=True)
    
    alertes = []
    if turnover > 15:
        alertes.append(("🔴 CRITIQUE", f"Turnover élevé: {turnover:.1f}% (Seuil > 15%)", "Plan de rétention urgent"))
    if fuite_cadres > 10:
        alertes.append(("🔴 CRITIQUE", f"Fuite des cadres: {fuite_cadres:.1f}% (Seuil > 10%)", "Entretiens de départ"))
    elif fuite_cadres > 5:
        alertes.append(("🟡 ATTENTION", f"Fuite des cadres: {fuite_cadres:.1f}% (Seuil > 5%)", "Surveiller les départs"))
    if qualite < 80:
        alertes.append(("🟡 ATTENTION", f"Qualité recrutements: {qualite:.1f}% (Seuil < 80%)", "Améliorer processus d'intégration"))
    if taux_depart_1ere > 20:
        alertes.append(("🔴 CRITIQUE", f"Départs 1ère année: {taux_depart_1ere:.1f}% (Seuil > 20%)", "Revoir programme d'intégration"))
    if len(contrats_alertes) > 0:
        alertes.append(("🟡 ATTENTION", f"{len(contrats_alertes)} contrat(s) expire(nt) dans 30 jours", "Contacter les responsables"))
    
    if alertes:
        st.subheader(f"🚨 {len(alertes)} alerte(s) détectée(s)")
        for niveau, message, action in alertes:
            if "🔴" in niveau:
                st.markdown(f'<div class="alert-modern" style="border-left-color: #ef4444;">{niveau}<br><strong>{message}</strong><br>📋 {action}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert-modern" style="border-left-color: #f59e0b;">{niveau}<br><strong>{message}</strong><br>📋 {action}</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="modern-card" style="background: #d1fae5; text-align: center;">
            ✅ Aucune alerte critique. Tous les indicateurs sont sous contrôle.
        </div>
        """, unsafe_allow_html=True)

# ==================== PAGE CONFIGURATION ====================
elif page == "⚙️ Configuration":
    st.markdown("""
    <div class="glass-header">
        <h1 style="margin: 0;">⚙️ Configuration</h1>
        <p>Paramétrage de l'application</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Section 1: Profil utilisateur
    st.markdown("""
    <div class="config-section">
        <div class="config-title">👤 Profil Utilisateur</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Nom d'utilisateur", value="Admin RH", key="config_username")
        st.text_input("Email", value="admin@pratique-electronique.com", key="config_email")
    with col2:
        st.selectbox("Rôle", ["Administrateur", "Manager RH", "Consultant", "Visiteur"], key="config_role")
        st.selectbox("Langue", ["Français", "English", "العربية"], key="config_langue")
    
    # Section 2: Apparence
    st.markdown("""
    <div class="config-section">
        <div class="config-title">🎨 Apparence</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        theme = st.selectbox("Thème", ["Clair", "Sombre", "Système"], key="config_theme")
        st.color_picker("Couleur principale", "#0ea5e9", key="config_primary_color")
    with col2:
        st.selectbox("Police", ["Inter", "Poppins", "Roboto", "Open Sans"], key="config_font")
        st.slider("Taille des graphiques", 300, 600, 450, key="config_chart_size")
    
    # Section 3: Notifications
    st.markdown("""
    <div class="config-section">
        <div class="config-title">🔔 Notifications</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.checkbox("Alertes email pour turnover élevé", value=True, key="config_alert_turnover")
        st.checkbox("Alertes email pour contrats expirant", value=True, key="config_alert_contrats")
    with col2:
        st.checkbox("Rapport mensuel automatique", value=False, key="config_rapport_mensuel")
        st.checkbox("Notifications dans l'application", value=True, key="config_notifications")
    
    # Section 4: Logo
    st.markdown("""
    <div class="config-section">
        <div class="config-title">🖼️ Logo</div>
    </div>
    """, unsafe_allow_html=True)
    
    if LOGO_BASE64:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 1rem;">
            <img src="data:image/png;base64,{LOGO_BASE64}" style="width: 80px; height: 80px; border-radius: 1rem; border: 2px solid #e2e8f0;">
            <div>
                <p style="color: #10b981;">✅ Logo actuel</p>
                <p style="color: #64748b; font-size: 0.8rem;">Pour changer le logo, remplacez le fichier logo.png dans le dossier</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Aucun logo trouvé. Ajoutez un fichier logo.png dans le dossier.")
        st.file_uploader("Uploader un nouveau logo", type=["png", "jpg", "jpeg"], key="config_logo_upload")
    
    # Section 5: Base de données
    st.markdown("""
    <div class="config-section">
        <div class="config-title">💾 Base de données</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Source de données", value="Fichier local (CSV)", key="config_data_source", disabled=True)
    with col2:
        st.text_input("Dernière mise à jour", value=datetime.now().strftime("%d/%m/%Y %H:%M"), key="config_last_update", disabled=True)
    
    if st.button("🔄 Synchroniser les données", use_container_width=True, key="config_sync"):
        st.success("✅ Synchronisation terminée avec succès!")
        st.cache_data.clear()
        st.rerun()
    
    # Section 6: Sauvegarde
    st.markdown("""
    <div class="config-section">
        <div class="config-title">💾 Sauvegarde</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Exporter la configuration", use_container_width=True, key="config_export"):
            st.success("Configuration exportée avec succès!")
    with col2:
        if st.button("📤 Importer la configuration", use_container_width=True, key="config_import"):
            st.info("Veuillez sélectionner un fichier de configuration")
    
    # Bouton sauvegarde
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("💾 Enregistrer tous les paramètres", use_container_width=True, key="config_save_all"):
            st.success("✅ Tous les paramètres ont été enregistrés avec succès!")
            st.balloons()
