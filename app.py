import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="HR Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== STYLE DATA-DRIVEN ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: #f8fafc;
    }
    
    .dashboard-header {
        background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%);
        padding: 2rem;
        border-radius: 0px;
        margin-bottom: 2rem;
        border-bottom: 3px solid #3b82f6;
    }
    
    .metric-card-dark {
        background: white;
        border-radius: 1rem;
        padding: 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        transition: all 0.2s;
    }
    
    .metric-card-dark:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    
    .metric-value-large {
        font-size: 2rem;
        font-weight: 700;
        color: #0f172a;
    }
    
    .metric-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        font-weight: 600;
    }
    
    .trend-up {
        color: #10b981;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .trend-down {
        color: #ef4444;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .alert-critical {
        background: #fef2f2;
        border-left: 4px solid #dc2626;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
        color: #991b1b;
    }
    
    .alert-warning {
        background: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
        color: #92400e;
    }
    
    .success-card {
        background: #f0fdf4;
        border-left: 4px solid #22c55e;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
        color: #166534;
    }
    
    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #0f172a;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }
    
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    hr {
        margin: 2rem 0;
    }
    
    /* Sidebar style */
    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== DONNÉES (MÊMES) ====================
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
    niveau = "Faible" if score_risque < 10 else "Moyen" if score_risque < 20 else "Élevé"
    services_risque.append({'Service': service, 'Score Risque': round(score_risque, 1), 'Niveau': niveau})

date_limite = datetime.now() + timedelta(days=30)
contrats_alertes = contrats_expiration[contrats_expiration['Date_Fin'] <= date_limite]

# ==================== SIDEBAR DATA-DRIVEN ====================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <div style="background: #3b82f6; width: 50px; height: 50px; border-radius: 12px; margin: 0 auto; display: flex; align-items: center; justify-content: center;">
            <span style="font-size: 1.5rem; color: white;">HR</span>
        </div>
        <h4 style="margin: 0.5rem 0 0 0; color: #0f172a;">HR Analytics</h4>
        <p style="color: #64748b; font-size: 0.7rem;">Data-Driven Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filtres
    st.markdown("### Filters")
    service_filter = st.multiselect("Service", actifs['Service'].unique(), default=actifs['Service'].unique())
    categorie_filter = st.multiselect("Category", actifs['Categorie'].unique(), default=actifs['Categorie'].unique())
    
    st.markdown("---")
    page = st.radio("Navigation", ["Dashboard", "Mouvements", "Talents", "Administration", "KPIs", "Alerts"])
    
    st.markdown("---")
    st.caption("© 2025 HR Analytics")
    st.caption("Version 2.0 | Data-Driven")

# ==================== PAGE DASHBOARD ====================
if page == "Dashboard":
    st.markdown("""
    <div class="dashboard-header">
        <h1 style="margin: 0; color: white;">HR Analytics Dashboard</h1>
        <p style="color: #94a3b8; margin-top: 0.5rem;">Real-time HR metrics and workforce analytics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # KPI Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card-dark">
            <div class="metric-label">TOTAL HEADCOUNT</div>
            <div class="metric-value-large">{total}</div>
            <div class="trend-up">▲ +{total-15} this year</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card-dark">
            <div class="metric-label">TURNOVER RATE</div>
            <div class="metric-value-large">{turnover:.1f}%</div>
            <div class="trend-down">▼ Target: {'✓' if turnover < 15 else '&lt;15%'}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card-dark">
            <div class="metric-label">PROMOTIONS</div>
            <div class="metric-value-large">{len(promotions)}</div>
            <div class="trend-up">▲ +33% vs 2023</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card-dark">
            <div class="metric-label">DEPARTURES</div>
            <div class="metric-value-large">{departs}</div>
            <div class="trend-down">▼ -2 vs 2023</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        effectifs_filtres = actifs[actifs['Service'].isin(service_filter) & actifs['Categorie'].isin(categorie_filter)]
        effectifs_service = effectifs_filtres.groupby('Service').size().reset_index(name='Effectif')
        fig = px.bar(effectifs_service, x='Service', y='Effectif', title="Workforce by Department",
                     color='Effectif', color_continuous_scale='Blues')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=mouvements['Mois'].dt.strftime('%b %Y'), y=mouvements['Entrees'].cumsum(),
                                 name='Cumulative Hires', mode='lines+markers', line=dict(color='#10b981', width=3)))
        fig.add_trace(go.Scatter(x=mouvements['Mois'].dt.strftime('%b %Y'), y=mouvements['Total_Sorties'].cumsum(),
                                 name='Cumulative Departures', mode='lines+markers', line=dict(color='#ef4444', width=3)))
        fig.update_layout(title="Cumulative Hires vs Departures", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Demographics
    st.markdown('<div class="section-title">Workforce Demographics</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card-dark">
            <div class="metric-label">CADRES</div>
            <div class="metric-value-large">{len(cadres)}</div>
            <div>{len(cadres)/total*100:.0f}% of total</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card-dark">
            <div class="metric-label">FEMALES</div>
            <div class="metric-value-large">{len(actifs[actifs['Sexe']=='F'])}</div>
            <div>{len(actifs[actifs['Sexe']=='F'])/total*100:.0f}% of total</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card-dark">
            <div class="metric-label">MALES</div>
            <div class="metric-value-large">{len(actifs[actifs['Sexe']=='H'])}</div>
            <div>{len(actifs[actifs['Sexe']=='H'])/total*100:.0f}% of total</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card-dark">
            <div class="metric-label">RESPONSE RATE</div>
            <div class="metric-value-large">{questionnaires['Taux_Reponse'].mean():.0f}%</div>
            <div>Survey participation</div>
        </div>
        """, unsafe_allow_html=True)

# ==================== PAGE MOUVEMENTS ====================
elif page == "Mouvements":
    st.markdown("""
    <div class="dashboard-header">
        <h1 style="margin: 0; color: white;">Workforce Movements</h1>
        <p>Hires, departures and turnover analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Hires", mouvements['Entrees'].sum())
    with col2:
        st.metric("Total Departures", mouvements['Total_Sorties'].sum())
    with col3:
        st.metric("Net Change", mouvements['Entrees'].sum() - mouvements['Total_Sorties'].sum())
    with col4:
        st.metric("Turnover Rate", f"{turnover:.1f}%")
    
    # Chart
    fig = go.Figure()
    fig.add_trace(go.Bar(x=mouvements['Mois'].dt.strftime('%b %Y'), y=mouvements['Entrees'], name='Hires', marker_color='#10b981'))
    fig.add_trace(go.Bar(x=mouvements['Mois'].dt.strftime('%b %Y'), y=mouvements['Total_Sorties'], name='Departures', marker_color='#ef4444'))
    fig.update_layout(title="Monthly Hires vs Departures", barmode='group', height=450)
    st.plotly_chart(fig, use_container_width=True)
    
    # Reasons
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card-dark">
            <div class="metric-label">RESIGNATIONS</div>
            <div class="metric-value-large">{mouvements['Sorties_Dem'].sum()}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card-dark">
            <div class="metric-label">RETIREMENTS</div>
            <div class="metric-value-large">{mouvements['Sorties_Retr'].sum()}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card-dark">
            <div class="metric-label">TERMINATIONS</div>
            <div class="metric-value-large">{mouvements['Sorties_Lice'].sum()}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Turnover by department
    st.markdown('<div class="section-title">Turnover by Department</div>', unsafe_allow_html=True)
    turnover_service = []
    for service in actifs['Service'].unique():
        effectif_service = len(actifs[actifs['Service'] == service])
        departs_service = len(effectifs[(effectifs['Service'] == service) & (~effectifs['Date_Sortie'].isna())])
        taux = (departs_service / effectif_service * 100) if effectif_service > 0 else 0
        turnover_service.append({'Department': service, 'Turnover Rate (%)': round(taux, 1)})
    st.dataframe(pd.DataFrame(turnover_service), use_container_width=True)
    
    # First year departure rate
    st.markdown('<div class="section-title">First Year Departure Rate</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="metric-card-dark">
        <div class="metric-value-large">{taux_depart_1ere:.1f}%</div>
        <div>Target: {'✓ Achieved' if taux_depart_1ere < 20 else '&lt;20%'}</div>
        <progress value="{taux_depart_1ere}" max="100" style="width: 100%; height: 6px;"></progress>
    </div>
    """, unsafe_allow_html=True)

# ==================== PAGE TALENTS ====================
elif page == "Talents":
    st.markdown("""
    <div class="dashboard-header">
        <h1 style="margin: 0; color: white;">Talent Management</h1>
        <p>Promotions and internal mobility</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-card-dark">
            <div class="metric-label">TOTAL PROMOTIONS</div>
            <div class="metric-value-large">{len(promotions)}</div>
            <div>2024-2025 period</div>
        </div>
        """, unsafe_allow_html=True)
        st.dataframe(promotions, use_container_width=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card-dark">
            <div class="metric-label">AVG PROMOTION DELAY</div>
            <div class="metric-value-large">{delai_promotion:.1f}</div>
            <div>years</div>
            <div>Target: {'✓' if delai_promotion < 3 else '&lt;3 years'}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card-dark">
            <div class="metric-label">INTERNAL MOBILITY</div>
            <div class="metric-value-large">{len(promotions)}</div>
            <div>position changes</div>
        </div>
        """, unsafe_allow_html=True)
    
    if len(promotions) > 0:
        promotions_par_annee = promotions.groupby(promotions['Date_Promot'].dt.year).size().reset_index(name='Count')
        promotions_par_annee.columns = ['Year', 'Count']
        fig = px.bar(promotions_par_annee, x='Year', y='Count', title="Promotions by Year", text='Count')
        fig.update_traces(marker_color='#3b82f6', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE ADMINISTRATION ====================
elif page == "Administration":
    st.markdown("""
    <div class="dashboard-header">
        <h1 style="margin: 0; color: white;">Administrative Management</h1>
        <p>Surveys, appraisals, sanctions, and absenteeism</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Survey response rate
    st.markdown('<div class="section-title">📊 Survey Response Rate</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average Rate", f"{questionnaires['Taux_Reponse'].mean():.1f}%")
    with col2:
        st.metric("Total Surveys", questionnaires['Nb_Diffuses'].sum())
    with col3:
        st.metric("Total Responses", questionnaires['Nb_Reponses'].sum())
    
    fig = px.area(questionnaires, x='Periode', y='Taux_Reponse', title="Response Rate Evolution",
                  markers=True, line_shape='spline')
    fig.add_hline(y=75, line_dash="dash", line_color="#f59e0b")
    st.plotly_chart(fig, use_container_width=True)
    
    # Annual interviews
    st.markdown('<div class="section-title">📋 Annual Interviews</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Completion Rate", f"{entretiens['Taux_Realisation'].mean():.1f}%")
    with col2:
        st.metric("Planned", entretiens['Nb_Planifies'].sum())
    with col3:
        st.metric("Completed", entretiens['Nb_Realises'].sum())
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=entretiens['Annee'], y=entretiens['Taux_Realisation'], 
                         text=entretiens['Taux_Realisation'], texttemplate='%{text:.1f}%'))
    fig.add_hline(y=80, line_dash="dash", line_color="#ef4444")
    fig.update_layout(title="Interview Completion Rate", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Contracts
    st.markdown('<div class="section-title">⚠️ Expiring Contracts (30 days)</div>', unsafe_allow_html=True)
    if len(contrats_alertes) > 0:
        st.markdown(f'<div class="alert-critical">🚨 {len(contrats_alertes)} contract(s) expiring within 30 days</div>', unsafe_allow_html=True)
        st.dataframe(contrats_alertes, use_container_width=True)
    else:
        st.markdown('<div class="success-card">✅ No contracts expiring in the next 30 days</div>', unsafe_allow_html=True)
    
    # Sanctions
    st.markdown('<div class="section-title">⚖️ Disciplinary Sanctions</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(sanctions, use_container_width=True)
    with col2:
        sanctions_par_service = sanctions.groupby('Service').size().reset_index(name='Count')
        fig = px.pie(sanctions_par_service, values='Count', names='Service', title="Sanctions by Department")
        st.plotly_chart(fig, use_container_width=True)
    
    # Absenteeism
    st.markdown('<div class="section-title">📊 Absenteeism Rate by Department</div>', unsafe_allow_html=True)
    fig = px.bar(absenteisme, x='Service', y='Taux_Absence', title="Absenteeism Rate",
                 color='Taux_Absence', color_continuous_scale=['#10b981', '#f59e0b', '#ef4444'])
    fig.add_hline(y=8, line_dash="dash", line_color="#ef4444", annotation_text="Alert Threshold 8%")
    st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE KPIs ====================
elif page == "KPIs":
    st.markdown("""
    <div class="dashboard-header">
        <h1 style="margin: 0; color: white;">Strategic KPIs</h1>
        <p>HR performance metrics and risk scores</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=qualite,
            title={'text': "Recruitment Quality"},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "#10b981"},
                   'steps': [{'range': [0, 50], 'color': '#fee2e2'},
                             {'range': [50, 80], 'color': '#fed7aa'},
                             {'range': [80, 100], 'color': '#d1fae5'}]}))
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=fuite_cadres,
            title={'text': "Talent Attrition"},
            gauge={'axis': {'range': [0, 30]},
                   'bar': {'color': "#ef4444"},
                   'steps': [
