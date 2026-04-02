import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="RH Dashboard - La Pratique Electronique",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== STYLE MODERNE ====================
st.markdown("""
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
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        border: 1px solid rgba(102, 126, 234, 0.15);
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
        font-size: 0.85rem;
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
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
        color: #333;
        font-weight: 500;
    }
    
    .success-card {
        background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
        color: white;
        font-weight: 500;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    .trend-up {
        color: #51cf66;
        font-weight: bold;
        font-size: 0.8rem;
    }
    
    .trend-down {
        color: #ff6b6b;
        font-weight: bold;
        font-size: 0.8rem;
    }
    
    .section-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
        display: inline-block;
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
    
    /* Style pour le logo dans sidebar */
    .sidebar-logo {
        text-align: center;
        margin-bottom: 20px;
        padding: 10px;
    }
    .sidebar-logo img {
        width: 80px;
        height: 80px;
        border-radius: 20px;
        object-fit: cover;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
        border: 2px solid rgba(102, 126, 234, 0.3);
    }
</style>
""", unsafe_allow_html=True)

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
    mouvements['Total_Sorties'] = mouvements['Sorties_Dem'] + mouvements['Sorties_Retr'] + mouvements['Sorties_Lice']
    
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

# ==================== SIDEBAR AVEC LOGO ====================
with st.sidebar:
    # Logo en haut du sidebar
    st.markdown("""
    <div class="sidebar-logo">
        <img src="https://raw.githubusercontent.com/souhaferjani-glitch/RH-Dashboard/main/logo.PNG" alt="Logo">
        <h3 style="color: #667eea; margin: 10px 0 0 0;">RH Dashboard</h3>
        <p style="color: #6c757d; font-size: 0.7rem;">La Pratique Electronique</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    service_filter = st.multiselect("🏢 Service", actifs['Service'].unique(), default=actifs['Service'].unique())
    categorie_filter = st.multiselect("⭐ Catégorie", actifs['Categorie'].unique(), default=actifs['Categorie'].unique())
    
    st.markdown("---")
    page = st.radio("📑 Navigation", [
        "🏠 Accueil", 
        "📈 Mouvements", 
        "⭐ Talents", 
        "⚙️ Administration", 
        "🎯 KPIs", 
        "⚠️ Alertes"
    ])
    
    st.markdown("---")
    st.caption("© 2025 - La Pratique Electronique")
    st.caption("Souha Ferjani | Projet PFE")

# ==================== PAGE ACCUEIL ====================
if page == "🏠 Accueil":
    st.markdown('<div class="main-header"><h1>📊 Tableau de Bord RH</h1><p>La Pratique Electronique - Suivi des indicateurs clés</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{total}</div>
            <div class="metric-label">👥 Effectif Total</div>
            <div class="trend-up">▲ +{total-15} cette année</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{turnover:.1f}%</div>
            <div class="metric-label">📈 Taux de Rotation</div>
            <div class="trend-down">▼ Objectif: <15%</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{len(promotions)}</div>
            <div class="metric-label">⭐ Promotions</div>
            <div class="trend-up">▲ +33% vs 2023</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{departs}</div>
            <div class="metric-label">🚪 Départs</div>
            <div class="trend-down">▼ -2 vs 2023</div>
        </div>
        ''', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        effectifs_filtres = actifs[actifs['Service'].isin(service_filter) & actifs['Categorie'].isin(categorie_filter)]
        effectifs_service = effectifs_filtres.groupby('Service').size().reset_index(name='Effectif')
        fig = px.pie(effectifs_service, values='Effectif', names='Service', 
                     title="🏢 Répartition par Service",
                     hole=0.4, 
                     color_discrete_sequence=px.colors.qualitative.Set3)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=450)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=mouvements['Mois'].dt.strftime('%b %Y'), y=mouvements['Entrees'], 
                             name='Entrées', marker_color='#51cf66',
                             text=mouvements['Entrees'], textposition='outside'))
        fig.add_trace(go.Bar(x=mouvements['Mois'].dt.strftime('%b %Y'), y=mouvements['Total_Sorties'], 
                             name='Sorties', marker_color='#ff6b6b',
                             text=mouvements['Total_Sorties'], textposition='outside'))
        fig.update_layout(title='📊 Entrées vs Sorties mensuelles', barmode='group', height=450)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('<div class="section-title">📊 Démographie</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👨‍💼 Cadres", len(cadres), delta=f"{len(cadres)/total*100:.0f}%")
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
        st.markdown(f'<div class="metric-card"><div class="metric-value">{mouvements["Entrees"].sum()}</div><div class="metric-label">📥 Total Entrées</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{mouvements["Total_Sorties"].sum()}</div><div class="metric-label">📤 Total Sorties</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{mouvements["Entrees"].sum() - mouvements["Total_Sorties"].sum()}</div><div class="metric-label">⚖️ Solde Net</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{turnover:.1f}%</div><div class="metric-label">🔄 Turnover</div></div>', unsafe_allow_html=True)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=mouvements['Mois'].dt.strftime('%b %Y'), y=mouvements['Entrees'], 
                         name='Entrées', marker_color='#51cf66', text=mouvements['Entrees'], textposition='outside'))
    fig.add_trace(go.Bar(x=mouvements['Mois'].dt.strftime('%b %Y'), y=mouvements['Total_Sorties'], 
                         name='Sorties', marker_color='#ff6b6b', text=mouvements['Total_Sorties'], textposition='outside'))
    fig.update_layout(title='Entrées vs Sorties mensuelles', barmode='group', height=450)
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📊 Motifs de sortie")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📝 Démission", mouvements['Sorties_Dem'].sum())
    with col2:
        st.metric("👴 Retraite", mouvements['Sorties_Retr'].sum())
    with col3:
        st.metric("⚖️ Licenciement", mouvements['Sorties_Lice'].sum())
    
    st.subheader("📊 Taux de départ en première année")
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{taux_depart_1ere:.1f}%</div>
        <div class="metric-label">Objectif: < 20%</div>
        <progress value="{taux_depart_1ere}" max="100" style="width: 100%; height: 8px; border-radius: 4px;"></progress>
    </div>
    """, unsafe_allow_html=True)

# ==================== PAGE TALENTS ====================
elif page == "⭐ Talents":
    st.markdown('<div class="main-header"><h1>⭐ Gestion des Talents</h1><p>Promotions et mobilité interne</p></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(promotions)}</div><div class="metric-label">⭐ Total Promotions</div></div>', unsafe_allow_html=True)
        st.dataframe(promotions, use_container_width=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{delai_promotion:.1f}</div><div class="metric-label">⏱️ Délai moyen de promotion (ans)</div><div class="trend-up">Objectif: {"✓" if delai_promotion < 3 else "< 3 ans"}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(promotions)}</div><div class="metric-label">🔄 Mobilité interne</div><div class="metric-label">Période: 2024-2025</div></div>', unsafe_allow_html=True)
    
    if len(promotions) > 0:
        promotions_par_annee = promotions.groupby(promotions['Date_Promot'].dt.year).size().reset_index(name='Nombre')
        promotions_par_annee.columns = ['Année', 'Nombre']
        fig = px.bar(promotions_par_annee, x='Année', y='Nombre', title="Promotions par année", text='Nombre')
        fig.update_traces(marker_color='#667eea', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE ADMINISTRATION ====================
elif page == "⚙️ Administration":
    st.markdown('<div class="main-header"><h1>⚙️ Gestion Administrative</h1><p>Suivi des indicateurs administratifs RH</p></div>', unsafe_allow_html=True)
    
    st.subheader("📊 Taux de réponse aux questionnaires")
    taux_reponse_moyen = questionnaires['Taux_Reponse'].mean()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Taux moyen", f"{taux_reponse_moyen:.1f}%")
    with col2:
        st.metric("Questionnaires diffusés", questionnaires['Nb_Diffuses'].sum())
    with col3:
        st.metric("Réponses reçues", questionnaires['Nb_Reponses'].sum())
    
    fig = px.line(questionnaires, x='Periode', y='Taux_Reponse', title="Évolution du taux de participation", markers=True)
    fig.add_hline(y=75, line_dash="dash", line_color="#f59e0b")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📋 Entretiens annuels")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Taux de réalisation", f"{entretiens['Taux_Realisation'].mean():.1f}%")
    with col2:
        st.metric("Planifiés", entretiens['Nb_Planifies'].sum())
    with col3:
        st.metric("Réalisés", entretiens['Nb_Realises'].sum())
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=entretiens['Annee'], y=entretiens['Taux_Realisation'], text=entretiens['Taux_Realisation'], texttemplate='%{text:.1f}%'))
    fig.add_hline(y=80, line_dash="dash", line_color="#ef4444")
    fig.update_layout(title="Taux de réalisation des entretiens annuels", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("⚠️ Contrats arrivant à expiration (30 jours)")
    if len(contrats_alertes) > 0:
        st.markdown(f'<div class="alert-critical">🚨 {len(contrats_alertes)} contrat(s) expire(nt) dans les 30 jours</div>', unsafe_allow_html=True)
        st.dataframe(contrats_alertes, use_container_width=True)
    else:
        st.markdown('<div class="success-card">✅ Aucun contrat n\'expire dans les 30 jours</div>', unsafe_allow_html=True)
    
    st.subheader("⚖️ Sanctions disciplinaires")
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(sanctions, use_container_width=True)
    with col2:
        sanctions_par_service = sanctions.groupby('Service').size().reset_index(name='Nb_Sanctions')
        fig = px.pie(sanctions_par_service, values='Nb_Sanctions', names='Service', title="Sanctions par service", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📊 Taux d'absentéisme par service")
    fig = px.bar(absenteisme, x='Service', y='Taux_Absence', title="Taux d'absentéisme", text='Taux_Absence')
    fig.add_hline(y=8, line_dash="dash", line_color="#ef4444", annotation_text="Seuil d'alerte 8%")
    st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE KPIs ====================
elif page == "🎯 KPIs":
    st.markdown('<div class="main-header"><h1>🎯 Indicateurs Stratégiques</h1><p>Performance RH et score de risque</p></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=qualite,
            title={'text': "Qualité des recrutements"},
            gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#51cf66"},
                   'steps': [{'range': [0, 50], 'color': '#ff6b6b'},
                             {'range': [50, 80], 'color': '#ffd93d'},
                             {'range': [80, 100], 'color': '#51cf66'}]}))
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=fuite_cadres,
            title={'text': "Fuite des compétences"},
            gauge={'axis': {'range': [0, 30]}, 'bar': {'color': "#ff6b6b"},
                   'steps': [{'range': [0, 5], 'color': '#51cf66'},
                             {'range': [5, 10], 'color': '#ffd93d'},
                             {'range': [10, 30], 'color': '#ff6b6b'}]}))
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("🎯 Score de risque par service")
    st.dataframe(pd.DataFrame(services_risque), use_container_width=True)
    
    fig = px.bar(pd.DataFrame(services_risque), x='Service', y='Score Risque', 
                 title="Score de risque par service", color='Score Risque',
                 color_continuous_scale=['#51cf66', '#ffd93d', '#ff6b6b'])
    st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE ALERTES ====================
elif page == "⚠️ Alertes":
    st.markdown('<div class="main-header"><h1>⚠️ Système d\'Alertes</h1><p>Détection automatique des risques</p></div>', unsafe_allow_html=True)
    
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
    if questionnaires['Taux_Reponse'].mean() < 50:
        alertes.append(("🟡 ATTENTION", f"Taux réponse questionnaires: {questionnaires['Taux_Reponse'].mean():.1f}%", "Relancer les enquêtes"))
    if entretiens['Taux_Realisation'].mean() < 80:
        alertes.append(("🟡 ATTENTION", f"Entretiens annuels: {entretiens['Taux_Realisation'].mean():.1f}%", "Planifier les entretiens manquants"))
    if len(contrats_alertes) > 0:
        alertes.append(("🟡 ATTENTION", f"{len(contrats_alertes)} contrat(s) expire(nt) dans 30 jours", "Contacter les responsables"))
    
    if alertes:
        st.subheader(f"🚨 {len(alertes)} alerte(s) détectée(s)")
        for niveau, message, action in alertes:
            if "🔴" in niveau:
                st.markdown(f'<div class="alert-critical">{niveau}<br><strong>{message}</strong><br>📋 Action: {action}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert-warning">{niveau}<br><strong>{message}</strong><br>📋 Action: {action}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="success-card">✅ Aucune alerte critique. Tous les indicateurs sont sous contrôle.</div>', unsafe_allow_html=True)
