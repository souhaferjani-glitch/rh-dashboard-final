import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="HR Dashboard - La Pratique Electronique",
    page_icon="📊",
    layout="wide"
)

# Style CSS
st.markdown("""
<style>
    .dashboard-header {
        background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%);
        padding: 2rem;
        margin-bottom: 2rem;
        border-bottom: 3px solid #3b82f6;
        border-radius: 10px;
    }
    .metric-card {
        background: white;
        border-radius: 1rem;
        padding: 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #0f172a;
    }
    .metric-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        color: #64748b;
        font-weight: 600;
    }
    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        margin: 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
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

# Score de risque par service
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
    st.markdown("### 📊 HR Analytics Dashboard")
    st.markdown("---")
    st.markdown("**La Pratique Electronique**")
    st.markdown("---")
    page = st.radio("Navigation", ["🏠 Dashboard", "📈 Mouvements", "⭐ Talents", "⚙️ Administration", "🎯 KPIs", "⚠️ Alertes"])
    st.markdown("---")
    st.caption("© 2025 - Souha Ferjani")

# ==================== PAGE DASHBOARD ====================
if page == "🏠 Dashboard":
    st.markdown('<div class="dashboard-header"><h1 style="color:white;">📊 RH Analytics Dashboard</h1><p style="color:#94a3b8;">Tableau de bord RH en temps réel</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">👥 EFFECTIF TOTAL</div><div class="metric-value">{total}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">🔄 TAUX TURNOVER</div><div class="metric-value">{turnover:.1f}%</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">⭐ PROMOTIONS</div><div class="metric-value">{len(promotions)}</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">🚪 DÉPARTS</div><div class="metric-value">{departs}</div></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        effectifs_service = actifs.groupby('Service').size().reset_index(name='Effectif')
        fig = px.pie(effectifs_service, values='Effectif', names='Service', title="🏢 Répartition par Service", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=mouvements['Mois'].dt.strftime('%b %Y'), y=mouvements['Entrees'], name='Entrées', marker_color='#10b981'))
        fig.add_trace(go.Bar(x=mouvements['Mois'].dt.strftime('%b %Y'), y=mouvements['Total_Sorties'], name='Sorties', marker_color='#ef4444'))
        fig.update_layout(title="📊 Entrées vs Sorties", barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('<div class="section-title">📊 Démographie</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👨‍💼 Cadres", len(cadres), delta=f"{len(cadres)/total*100:.0f}%")
    with col2:
        st.metric("👩 Femmes", len(actifs[actifs['Sexe']=='F']), delta=f"{len(actifs[actifs['Sexe']=='F'])/total*100:.0f}%")
    with col3:
        st.metric("👨 Hommes", len(actifs[actifs['Sexe']=='H']), delta=f"{len(actifs[actifs['Sexe']=='H'])/total*100:.0f}%")

# ==================== PAGE MOUVEMENTS ====================
elif page == "📈 Mouvements":
    st.markdown('<div class="dashboard-header"><h1 style="color:white;">📈 Mouvements du Personnel</h1></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📥 Total Entrées", mouvements['Entrees'].sum())
    with col2:
        st.metric("📤 Total Sorties", mouvements['Total_Sorties'].sum())
    with col3:
        st.metric("🔄 Turnover", f"{turnover:.1f}%")
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=mouvements['Mois'].dt.strftime('%b %Y'), y=mouvements['Entrees'], name='Entrées', marker_color='#10b981'))
    fig.add_trace(go.Bar(x=mouvements['Mois'].dt.strftime('%b %Y'), y=mouvements['Total_Sorties'], name='Sorties', marker_color='#ef4444'))
    fig.update_layout(title="Entrées vs Sorties mensuelles", barmode='group')
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📊 Motifs de départ")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📝 Démissions", mouvements['Sorties_Dem'].sum())
    with col2:
        st.metric("👴 Retraites", mouvements['Sorties_Retr'].sum())
    with col3:
        st.metric("⚖️ Licenciements", mouvements['Sorties_Lice'].sum())
    
    st.subheader("📊 Taux de départ en première année")
    st.metric("Taux", f"{taux_depart_1ere:.1f}%", delta="Objectif <20%")

# ==================== PAGE TALENTS ====================
elif page == "⭐ Talents":
    st.markdown('<div class="dashboard-header"><h1 style="color:white;">⭐ Gestion des Talents</h1></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("⭐ Total Promotions", len(promotions))
        st.dataframe(promotions, use_container_width=True)
    with col2:
        st.metric("⏱️ Délai moyen de promotion", f"{delai_promotion:.1f} ans")
        st.metric("🔄 Mobilité interne", f"{len(promotions)} changements")
    
    if len(promotions) > 0:
        promotions_par_annee = promotions.groupby(promotions['Date_Promot'].dt.year).size().reset_index(name='Nombre')
        promotions_par_annee.columns = ['Année', 'Nombre']
        fig = px.bar(promotions_par_annee, x='Année', y='Nombre', title="Promotions par année", text='Nombre')
        fig.update_traces(marker_color='#3b82f6', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE ADMINISTRATION ====================
elif page == "⚙️ Administration":
    st.markdown('<div class="dashboard-header"><h1 style="color:white;">⚙️ Gestion Administrative</h1></div>', unsafe_allow_html=True)
    
    st.subheader("📊 Taux de réponse aux questionnaires")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Taux moyen", f"{questionnaires['Taux_Reponse'].mean():.1f}%")
    with col2:
        st.metric("Questionnaires diffusés", questionnaires['Nb_Diffuses'].sum())
    with col3:
        st.metric("Réponses reçues", questionnaires['Nb_Reponses'].sum())
    
    fig = px.line(questionnaires, x='Periode', y='Taux_Reponse', title="Évolution du taux de réponse", markers=True)
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
    fig.update_layout(title="Taux de réalisation des entretiens")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("⚠️ Contrats arrivant à expiration (30 jours)")
    if len(contrats_alertes) > 0:
        st.error(f"🚨 {len(contrats_alertes)} contrat(s) expire(nt) dans les 30 jours")
        st.dataframe(contrats_alertes, use_container_width=True)
    else:
        st.success("✅ Aucun contrat n'expire dans les 30 jours")
    
    st.subheader("⚖️ Sanctions disciplinaires")
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(sanctions, use_container_width=True)
    with col2:
        sanctions_par_service = sanctions.groupby('Service').size().reset_index(name='Nb_Sanctions')
        fig = px.pie(sanctions_par_service, values='Nb_Sanctions', names='Service', title="Sanctions par service")
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📊 Taux d'absentéisme par service")
    fig = px.bar(absenteisme, x='Service', y='Taux_Absence', title="Taux d'absentéisme", text='Taux_Absence')
    fig.add_hline(y=8, line_dash="dash", line_color="#ef4444", annotation_text="Seuil d'alerte 8%")
    st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE KPIs ====================
elif page == "🎯 KPIs":
    st.markdown('<div class="dashboard-header"><h1 style="color:white;">🎯 Indicateurs Stratégiques</h1></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure(go.Indicator(mode="gauge+number", value=qualite, title="Qualité des recrutements", gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#10b981"}}))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = go.Figure(go.Indicator(mode="gauge+number", value=fuite_cadres, title="Fuite des compétences", gauge={'axis': {'range': [0, 30]}, 'bar': {'color': "#ef4444"}}))
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("🎯 Score de risque par service")
    st.dataframe(pd.DataFrame(services_risque), use_container_width=True)
    
    fig = px.bar(pd.DataFrame(services_risque), x='Service', y='Score Risque', title="Score de risque par service", color='Score Risque', color_continuous_scale=['#10b981', '#f59e0b', '#ef4444'])
    st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE ALERTES ====================
elif page == "⚠️ Alertes":
    st.markdown('<div class="dashboard-header"><h1 style="color:white;">⚠️ Système d\'Alerte</h1></div>', unsafe_allow_html=True)
    
    if turnover > 15:
        st.error(f"🔴 CRITIQUE - Turnover élevé: {turnover:.1f}% (Seuil > 15%)")
    else:
        st.success(f"✅ Turnover sous contrôle: {turnover:.1f}%")
    
    if fuite_cadres > 10:
        st.error(f"🔴 CRITIQUE - Fuite des cadres: {fuite_cadres:.1f}% (Seuil > 10%)")
    elif fuite_cadres > 5:
        st.warning(f"🟡 ATTENTION - Fuite des cadres: {fuite_cadres:.1f}% (Seuil > 5%)")
    else:
        st.success(f"✅ Fuite des cadres sous contrôle: {fuite_cadres:.1f}%")
    
    if qualite < 80:
        st.warning(f"🟡 ATTENTION - Qualité recrutements: {qualite:.1f}% (Seuil < 80%)")
    else:
        st.success(f"✅ Bonne qualité recrutements: {qualite:.1f}%")
    
    if taux_depart_1ere > 20:
        st.error(f"🔴 CRITIQUE - Départs 1ère année: {taux_depart_1ere:.1f}% (Seuil > 20%)")
    elif taux_depart_1ere > 15:
        st.warning(f"🟡 ATTENTION - Départs 1ère année: {taux_depart_1ere:.1f}% (Seuil > 15%)")
    
    if len(contrats_alertes) > 0:
        st.warning(f"🟡 ATTENTION - {len(contrats_alertes)} contrat(s) expire(nt) dans 30 jours")
