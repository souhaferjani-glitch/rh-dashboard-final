import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import time
import warnings
import base64
import os
import json
from pathlib import Path

warnings.filterwarnings('ignore')

# ==================== CONFIGURATION PAGE ====================
st.set_page_config(
    page_title="HR Analytics Platform - La Pratique Electronique",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== SESSION STATE INITIALISATION ====================
if "hr_settings" not in st.session_state:
    st.session_state.hr_settings = {
        "language": "fr",
        "theme_mode": "light",
        "accent_color": "#2E86AB",
        "font_style": "sans-serif",
        "chart_height": 400,
        "enable_alerts": True,
        "contract_alerts": True,
        "auto_report": False,
        "notify_email": True,
        "last_refresh": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = ""
    st.session_state.user_role = ""

# ==================== FONCTIONS UTILITAIRES ====================
def get_logo_base64():
    """Récupère le logo en base64"""
    logo_paths = ["logo.png", "logo.PNG", "assets/logo.png", "images/logo.png", "static/logo.png"]
    for path in logo_paths:
        if os.path.exists(path):
            with open(path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
    return None

LOGO_BASE64 = get_logo_base64()

def apply_theme():
    """Applique le thème sélectionné"""
    if st.session_state.hr_settings["theme_mode"] == "dark":
        st.markdown("""
        <style>
            .stApp { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); }
            .hr-card { background: rgba(255,255,255,0.05); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.1); }
            .hr-card:hover { border-color: rgba(46,134,171,0.5); background: rgba(255,255,255,0.08); }
            .metric-label { color: #a0aec0; }
            [data-testid="stSidebar"] { background: rgba(0,0,0,0.3); backdrop-filter: blur(10px); border-right: 1px solid rgba(255,255,255,0.1); }
            [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
            .config-panel { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); }
            .panel-title { color: #2E86AB; border-bottom-color: #2E86AB; }
            .stButton > button { background: linear-gradient(135deg, #2E86AB 0%, #1B4965 100%); }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
            .stApp { background: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%); }
            .hr-card { background: white; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
            .hr-card:hover { box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1); transform: translateY(-2px); }
            .metric-label { color: #64748b; }
            [data-testid="stSidebar"] { background: white; border-right: 1px solid #e2e8f0; }
            [data-testid="stSidebar"] * { color: #1e293b !important; }
            .config-panel { background: #f8fafc; border: 1px solid #e2e8f0; }
            .panel-title { color: #2E86AB; border-bottom-color: #e2e8f0; }
        </style>
        """, unsafe_allow_html=True)

# ==================== STYLES CSS ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .hr-header {
        background: linear-gradient(120deg, #2E86AB 0%, #1B4965 100%);
        padding: 1.5rem 2rem;
        border-radius: 1rem;
        color: white;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .hr-title h1 { margin: 0; font-size: 1.75rem; font-weight: 600; }
    .hr-title p { margin: 0.25rem 0 0 0; opacity: 0.9; font-size: 0.875rem; }
    
    .hr-card {
        border-radius: 1rem;
        padding: 1.25rem;
        transition: all 0.3s ease;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #2E86AB;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    .trend-positive { color: #10b981; font-size: 0.7rem; margin-top: 0.25rem; }
    .trend-negative { color: #ef4444; font-size: 0.7rem; margin-top: 0.25rem; }
    
    .alert-box-critical {
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
        padding: 1rem;
        border-radius: 0.75rem;
        color: white;
        margin: 0.75rem 0;
        animation: pulse 1.5s infinite;
    }
    
    .alert-box-warning {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        padding: 1rem;
        border-radius: 0.75rem;
        color: white;
        margin: 0.75rem 0;
    }
    
    .alert-box-success {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 1rem;
        border-radius: 0.75rem;
        color: white;
        margin: 0.75rem 0;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.02); opacity: 0.95; }
    }
    
    .section-divider {
        margin: 1.5rem 0;
        border-top: 2px solid #e2e8f0;
    }
    
    .config-panel {
        border-radius: 1rem;
        padding: 1.25rem;
        margin-bottom: 1.25rem;
    }
    
    .panel-title {
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid;
        display: inline-block;
    }
    
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.7rem;
        font-weight: 500;
    }
    
    .badge-success { background: #10b98120; color: #10b981; }
    .badge-warning { background: #f59e0b20; color: #f59e0b; }
    .badge-danger { background: #ef444420; color: #ef4444; }
    
    .stButton > button {
        border-radius: 0.5rem;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(46,134,171,0.3);
    }
    
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

apply_theme()

# ==================== LOGIN SYSTEM ====================
USERS_DB = {
    "rh_admin": {"password": "admin123", "role": "Administrateur"},
    "rh_manager": {"password": "manager1", "role": "Manager RH"},
    "consultant": {"password": "consult2", "role": "Consultant"}
}

def render_login():
    st.markdown("""
    <style>
        .login-wrapper {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 2rem;
        }
        .login-container {
            max-width: 900px;
            width: 100%;
            background: white;
            border-radius: 2rem;
            overflow: hidden;
            display: flex;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
        }
        .login-brand {
            flex: 1;
            background: linear-gradient(135deg, #2E86AB 0%, #1B4965 100%);
            padding: 3rem 2rem;
            text-align: center;
            color: white;
        }
        .login-brand h2 { font-size: 1.75rem; margin-bottom: 0.5rem; }
        .login-brand p { opacity: 0.9; font-size: 0.875rem; }
        .login-form {
            flex: 1;
            padding: 3rem 2rem;
            background: white;
        }
        .login-form h3 { color: #1e293b; margin-bottom: 1.5rem; }
        @media (max-width: 768px) {
            .login-container { flex-direction: column; max-width: 400px; }
        }
    </style>
    
    <div class="login-wrapper">
        <div class="login-container">
            <div class="login-brand">
                <div style="font-size: 4rem; margin-bottom: 1rem;">🎯</div>
                <h2>HR Analytics</h2>
                <p>La Pratique Electronique</p>
                <p style="margin-top: 1rem; font-size: 0.75rem;">Business Intelligence Platform</p>
            </div>
            <div class="login-form">
                <h3>🔐 Accès Sécurisé</h3>
    """, unsafe_allow_html=True)
    
    username = st.text_input("Identifiant", placeholder="hr_admin", key="login_user", label_visibility="collapsed")
    password = st.text_input("Mot de passe", type="password", placeholder="••••••••", key="login_pass", label_visibility="collapsed")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Se connecter", use_container_width=True):
            if username in USERS_DB and USERS_DB[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.current_user = username
                st.session_state.user_role = USERS_DB[username]["role"]
                st.rerun()
            else:
                st.error("❌ Identifiants invalides")
    
    st.markdown("""
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

if not st.session_state.logged_in:
    render_login()
    st.stop()

# ==================== CHARGEMENT DES DONNÉES ====================
@st.cache_data(ttl=3600)
def load_hr_data():
    """Charge toutes les données RH"""
    
    # Effectifs
    employees = pd.DataFrame({
        'ID': ['E001','E002','E003','E004','E005','E006','E007','E008','E009','E010','E011','E012','E013','E014','E015'],
        'Hire_Date': ['2020-01-01','2021-06-15','2022-03-10','2023-09-05','2021-01-20','2023-07-01','2022-11-15','2020-05-10','2024-02-01','2021-08-15','2023-03-20','2022-12-05','2021-07-10','2023-09-01','2022-04-15'],
        'Exit_Date': [None,'2024-12-01',None,None,'2024-10-15',None,'2025-03-31',None,None,None,'2025-02-28',None,None,None,'2025-01-15'],
        'Exit_Reason': [None,'Démission',None,None,'Retraite',None,'Démission',None,None,None,'Licenciement',None,None,None,'Démission'],
        'Department': ['Commercial','RH','Technical','Commercial','Admin','Technical','Commercial','RH','Technical','Admin','Commercial','Technical','RH','Commercial','Technical'],
        'Grade': ['Executive','Staff','Executive','Staff','Executive','Staff','Executive','Executive','Staff','Staff','Staff','Executive','Staff','Executive','Staff'],
        'Gender': ['M','F','M','F','M','F','F','F','M','F','M','M','F','M','F']
    })
    employees['Hire_Date'] = pd.to_datetime(employees['Hire_Date'])
    employees['Exit_Date'] = pd.to_datetime(employees['Exit_Date'], errors='coerce')
    
    # Mouvements mensuels
    movements = pd.DataFrame({
        'Month': ['2024-01-01','2024-02-01','2024-03-01','2024-04-01','2024-05-01','2024-06-01'],
        'Hires': [2,1,3,0,2,1],
        'Resignations': [1,0,2,1,0,2],
        'Retirements': [0,1,0,0,0,0],
        'Terminations': [0,0,1,0,0,0]
    })
    movements['Month'] = pd.to_datetime(movements['Month'])
    movements['Total_Exits'] = movements['Resignations'] + movements['Retirements'] + movements['Terminations']
    
    # Promotions
    promotions = pd.DataFrame({
        'ID': ['E001','E003','E008','E012'],
        'Promo_Date': ['2025-01-01','2024-03-15','2024-12-01','2024-06-10'],
        'Old_Role': ['Senior Commercial','Technician','HR Assistant','Engineer'],
        'New_Role': ['Commercial Director','Senior Technician','HR Manager','Principal Engineer']
    })
    promotions['Promo_Date'] = pd.to_datetime(promotions['Promo_Date'])
    
    # Enquêtes
    surveys = pd.DataFrame({
        'Period': ['01/2024','02/2024','03/2024','04/2024','05/2024','06/2024'],
        'Sent': [50,50,50,50,50,50],
        'Responses': [42,38,45,40,44,39],
        'Response_Rate': [84,76,90,80,88,78]
    })
    
    # Entretiens
    interviews = pd.DataFrame({
        'Year': [2023,2024,2025],
        'Planned': [20,22,15],
        'Completed': [18,19,13],
        'Completion_Rate': [90,86.4,86.7]
    })
    
    # Sanctions
    sanctions = pd.DataFrame({
        'Date': ['2024-01-15','2024-02-20','2024-03-10','2024-04-05','2024-05-12'],
        'Department': ['Commercial','Technical','RH','Commercial','Technical'],
        'Type': ['Warning','Reprimand','Warning','Suspension','Reprimand']
    })
    sanctions['Date'] = pd.to_datetime(sanctions['Date'])
    
    # Absentéisme
    absenteeism = pd.DataFrame({
        'Month': ['01/2024','02/2024','03/2024','04/2024','05/2024','06/2024'],
        'Department': ['Commercial','Technical','RH','Commercial','Technical','RH'],
        'Absence_Rate': [5.2,6.8,3.5,6.1,7.2,4.2]
    })
    
    # Contrats expirant
    expiring_contracts = pd.DataFrame({
        'ID': ['E004', 'E009', 'E014'],
        'End_Date': pd.to_datetime(['2026-04-15', '2026-04-20', '2026-05-01']),
        'Type': ['Fixed-term', 'Fixed-term', 'Fixed-term'],
        'Department': ['Commercial', 'Technical', 'Commercial']
    })
    
    return employees, movements, promotions, surveys, interviews, sanctions, absenteeism, expiring_contracts

employees, movements, promotions, surveys, interviews, sanctions, absenteeism, expiring_contracts = load_hr_data()

# ==================== INDICATEURS CLÉS ====================
def calculate_metrics():
    """Calcule tous les indicateurs RH"""
    
    active = employees[employees['Exit_Date'].isna()]
    total_active = len(active)
    total_exits = len(employees[~employees['Exit_Date'].isna()])
    turnover_rate = (total_exits / len(employees) * 100) if len(employees) > 0 else 0
    
    executives = employees[employees['Grade'] == 'Executive']
    executive_exits = len(executives[~executives['Exit_Date'].isna()])
    executive_leakage = (executive_exits / len(executives) * 100) if len(executives) > 0 else 0
    
    recent_hires = employees[employees['Hire_Date'] > datetime.now() - timedelta(days=365)]
    retention_quality = (len(recent_hires[recent_hires['Exit_Date'].isna()]) / len(recent_hires) * 100) if len(recent_hires) > 0 else 0
    
    first_year_exits = len(recent_hires[~recent_hires['Exit_Date'].isna()])
    first_year_rate = (first_year_exits / len(recent_hires) * 100) if len(recent_hires) > 0 else 0
    
    avg_promo_delay = 0
    if len(promotions) > 0:
        promo_with_hire = promotions.merge(employees[['ID', 'Hire_Date']], on='ID')
        promo_with_hire['Delay_Years'] = (promo_with_hire['Promo_Date'] - promo_with_hire['Hire_Date']).dt.days / 365.25
        avg_promo_delay = promo_with_hire['Delay_Years'].mean()
    
    # Score de risque par département
    risk_scores = []
    for dept in active['Department'].unique():
        dept_active = len(active[active['Department'] == dept])
        dept_exits = len(employees[(employees['Department'] == dept) & (~employees['Exit_Date'].isna())])
        dept_turnover = (dept_exits / dept_active * 100) if dept_active > 0 else 0
        
        dept_sanctions = len(sanctions[sanctions['Department'] == dept])
        sanction_rate = (dept_sanctions / dept_active * 100) if dept_active > 0 else 0
        
        dept_absences = absenteeism[absenteeism['Department'] == dept]['Absence_Rate'].mean() if dept in absenteeism['Department'].values else 0
        
        risk_score = (dept_turnover * 0.4) + (sanction_rate * 0.3) + (dept_absences * 0.3)
        risk_level = "Low" if risk_score < 10 else "Medium" if risk_score < 20 else "High"
        
        risk_scores.append({
            'Department': dept,
            'Turnover': round(dept_turnover, 1),
            'Sanctions': round(sanction_rate, 1),
            'Absenteeism': round(dept_absences, 1),
            'Risk_Score': round(risk_score, 1),
            'Level': risk_level
        })
    
    return {
        'total_active': total_active,
        'total_exits': total_exits,
        'turnover_rate': turnover_rate,
        'executive_count': len(executives),
        'executive_leakage': executive_leakage,
        'retention_quality': retention_quality,
        'first_year_rate': first_year_rate,
        'total_promotions': len(promotions),
        'avg_promo_delay': avg_promo_delay,
        'risk_scores': risk_scores,
        'female_count': len(active[active['Gender'] == 'F']),
        'male_count': len(active[active['Gender'] == 'M']),
        'avg_survey_rate': surveys['Response_Rate'].mean(),
        'avg_interview_rate': interviews['Completion_Rate'].mean()
    }

metrics = calculate_metrics()

# Alertes à 30 jours
alert_date = datetime.now() + timedelta(days=30)
contract_alerts = expiring_contracts[expiring_contracts['End_Date'] <= alert_date]

# ==================== SIDEBAR ====================
with st.sidebar:
    if LOGO_BASE64:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem 0;">
            <img src="data:image/png;base64,{LOGO_BASE64}" style="width: 70px; height: 70px; border-radius: 50%; margin-bottom: 0.5rem;">
            <h4 style="margin: 0; color: #2E86AB;">La Pratique</h4>
            <p style="font-size: 0.7rem; opacity: 0.7;">Electronique</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <div style="font-size: 3rem;">🎯</div>
            <h4 style="margin: 0;">HR Analytics</h4>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"**👤 {st.session_state.current_user}**")
    st.markdown(f"<span class='badge badge-success'>{st.session_state.user_role}</span>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Filtres
    dept_filter = st.multiselect(
        "🏢 Départements",
        employees['Department'].unique(),
        default=employees['Department'].unique()
    )
    
    grade_filter = st.multiselect(
        "⭐ Grades",
        employees['Grade'].unique(),
        default=employees['Grade'].unique()
    )
    
    gender_filter = st.multiselect(
        "👥 Genre",
        employees['Gender'].unique(),
        default=employees['Gender'].unique()
    )
    
    st.markdown("---")
    
    # Navigation
    nav_options = {
        "🏠 Dashboard": "dashboard",
        "📊 Analytics": "analytics",
        "👥 People": "people",
        "⚠️ Monitoring": "monitoring",
        "⚙️ Settings": "settings"
    }
    
    selected_page = st.radio(
        "Navigation",
        list(nav_options.keys()),
        key="nav_radio"
    )
    current_page = nav_options[selected_page]
    
    st.markdown("---")
    
    if st.button("📄 Export Report", use_container_width=True):
        st.info("Export en préparation...")
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.rerun()
    
    st.markdown("---")
    st.caption("© 2025 La Pratique Electronique")
    st.caption("v3.0 - HR Intelligence")

# ==================== PAGE DASHBOARD ====================
if current_page == "dashboard":
    # En-tête
    st.markdown(f"""
    <div class="hr-header">
        <div class="hr-title">
            <h1>🎯 HR Performance Dashboard</h1>
            <p>Vue d'ensemble des indicateurs clés - {datetime.now().strftime('%d %B %Y')}</p>
        </div>
        <div class="badge badge-success">🟢 Live Data</div>
    </div>
    """, unsafe_allow_html=True)
    
    # KPIs principaux
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="hr-card">
            <div class="metric-label">👥 Effectif Total</div>
            <div class="metric-value">{metrics['total_active']}</div>
            <div class="trend-positive">▲ +{metrics['total_active']-12} cette année</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="hr-card">
            <div class="metric-label">🔄 Turnover</div>
            <div class="metric-value">{metrics['turnover_rate']:.1f}%</div>
            <div class="trend-negative">▼ Cible: &lt;15%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="hr-card">
            <div class="metric-label">⭐ Promotions</div>
            <div class="metric-value">{metrics['total_promotions']}</div>
            <div class="trend-positive">▲ +33% vs 2023</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="hr-card">
            <div class="metric-label">🚪 Départs</div>
            <div class="metric-value">{metrics['total_exits']}</div>
            <div class="trend-negative">▼ -2 vs 2023</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    
    # Graphiques principaux
    col_left, col_right = st.columns(2)
    
    with col_left:
        # Répartition par département
        filtered_employees = employees[
            employees['Department'].isin(dept_filter) &
            employees['Grade'].isin(grade_filter) &
            employees['Gender'].isin(gender_filter) &
            employees['Exit_Date'].isna()
        ]
        dept_dist = filtered_employees.groupby('Department').size().reset_index(name='Count')
        
        fig1 = px.pie(
            dept_dist, 
            values='Count', 
            names='Department',
            title="📊 Distribution par Département",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig1.update_traces(textposition='inside', textinfo='percent+label')
        fig1.update_layout(height=st.session_state.hr_settings["chart_height"])
        st.plotly_chart(fig1, use_container_width=True)
    
    with col_right:
        # Évolution des effectifs
        cumulative_employees = []
        for i in range(len(movements)):
            cum_hires = movements['Hires'].iloc[:i+1].sum()
            cum_exits = movements['Total_Exits'].iloc[:i+1].sum()
            cumulative_employees.append(cum_hires - cum_exits)
        
        fig2 = px.area(
            x=movements['Month'].dt.strftime('%b %Y'),
            y=cumulative_employees,
            title="📈 Évolution des Effectifs",
            markers=True,
            color_discrete_sequence=['#2E86AB']
        )
        fig2.update_layout(xaxis_title="Mois", yaxis_title="Effectif", height=st.session_state.hr_settings["chart_height"])
        st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    
    # Démographie
    st.markdown("### 👥 Démographie RH")
    demo_col1, demo_col2, demo_col3, demo_col4 = st.columns(4)
    
    with demo_col1:
        st.markdown(f"""
        <div class="hr-card">
            <div class="metric-label">👨‍💼 Cadres</div>
            <div class="metric-value">{metrics['executive_count']}</div>
            <div>{metrics['executive_count']/metrics['total_active']*100:.0f}% du total</div>
        </div>
        """, unsafe_allow_html=True)
    
    with demo_col2:
        st.markdown(f"""
        <div class="hr-card">
            <div class="metric-label">👩 Femmes</div>
            <div class="metric-value">{metrics['female_count']}</div>
            <div>{metrics['female_count']/metrics['total_active']*100:.0f}% du total</div>
        </div>
        """, unsafe_allow_html=True)
    
    with demo_col3:
        st.markdown(f"""
        <div class="hr-card">
            <div class="metric-label">👨 Hommes</div>
            <div class="metric-value">{metrics['male_count']}</div>
            <div>{metrics['male_count']/metrics['total_active']*100:.0f}% du total</div>
        </div>
        """, unsafe_allow_html=True)
    
    with demo_col4:
        st.markdown(f"""
        <div class="hr-card">
            <div class="metric-label">📊 Taux Réponse</div>
            <div class="metric-value">{metrics['avg_survey_rate']:.0f}%</div>
            <div>Moyenne enquêtes</div>
        </div>
        """, unsafe_allow_html=True)

# ==================== PAGE ANALYTICS ====================
elif current_page == "analytics":
    st.markdown("""
    <div class="hr-header">
        <div class="hr-title">
            <h1>📊 HR Analytics Avancé</h1>
            <p>Analyse des mouvements et indicateurs stratégiques</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Mouvements
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="hr-card">
            <div class="metric-label">📥 Entrées</div>
            <div class="metric-value">{movements['Hires'].sum()}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="hr-card">
            <div class="metric-label">📤 Sorties</div>
            <div class="metric-value">{movements['Total_Exits'].sum()}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="hr-card">
            <div class="metric-label">⚖️ Solde Net</div>
            <div class="metric-value">{movements['Hires'].sum() - movements['Total_Exits'].sum()}</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="hr-card">
            <div class="metric-label">🔄 Turnover Global</div>
            <div class="metric-value">{metrics['turnover_rate']:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Graphique entrées/sorties
    fig_mov = go.Figure()
    fig_mov.add_trace(go.Bar(
        x=movements['Month'].dt.strftime('%b %Y'),
        y=movements['Hires'],
        name='Entrées',
        marker_color='#10b981',
        text=movements['Hires'],
        textposition='outside'
    ))
    fig_mov.add_trace(go.Bar(
        x=movements['Month'].dt.strftime('%b %Y'),
        y=movements['Total_Exits'],
        name='Sorties',
        marker_color='#ef4444',
        text=movements['Total_Exits'],
        textposition='outside'
    ))
    fig_mov.update_layout(
        title="Entrées vs Sorties Mensuelles",
        barmode='group',
        height=st.session_state.hr_settings["chart_height"]
    )
    st.plotly_chart(fig_mov, use_container_width=True)
    
    # Motifs de sortie
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="hr-card">
            <div class="metric-label">📝 Démissions</div>
            <div class="metric-value">{movements['Resignations'].sum()}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="hr-card">
            <div class="metric-label">👴 Retraites</div>
            <div class="metric-value">{movements['Retirements'].sum()}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="hr-card">
            <div class="metric-label">⚖️ Licenciements</div>
            <div class="metric-value">{movements['Terminations'].sum()}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Turnover par département
    st.markdown("### 📊 Turnover par Département")
    turnover_dept = []
    for dept in employees['Department'].unique():
        dept_active = len(employees[(employees['Department'] == dept) & (employees['Exit_Date'].isna())])
        dept_exits = len(employees[(employees['Department'] == dept) & (~employees['Exit_Date'].isna())])
        rate = (dept_exits / dept_active * 100) if dept_active > 0 else 0
        turnover_dept.append({'Département': dept, 'Turnover (%)': round(rate, 1), 'Départs': dept_exits})
    
    st.dataframe(pd.DataFrame(turnover_dept), use_container_width=True)
    
    # KPIs supplémentaires
    st.markdown("### 🎯 Indicateurs Stratégiques")
    
    kpi_col1, kpi_col2 = st.columns(2)
    
    with kpi_col1:
        fig_gauge1 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=metrics['retention_quality'],
            title={'text': "Qualité des Recrutements"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#2E86AB"},
                'steps': [
                    {'range': [0, 50], 'color': '#fee2e2'},
                    {'range': [50, 80], 'color': '#fed7aa'},
                    {'range': [80, 100], 'color': '#d1fae5'}
                ]
            }
        ))
        fig_gauge1.update_layout(height=350)
        st.plotly_chart(fig_gauge1, use_container_width=True)
    
    with kpi_col2:
        fig_gauge2 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=metrics['executive_leakage'],
            title={'text': "Fuite des Cadres"},
            gauge={
                'axis': {'range': [0, 30]},
                'bar': {'color': "#ef4444"},
                'steps': [
                    {'range': [0, 5], 'color': '#d1fae5'},
                    {'range': [5, 10], 'color': '#fed7aa'},
                    {'range': [10, 30], 'color': '#fee2e2'}
                ]
            }
        ))
        fig_gauge2.update_layout(height=350)
        st.plotly_chart(fig_gauge2, use_container_width=True)
    
    # Départs première année
    st.markdown("### 📊 Taux de Départ en Première Année")
    if len(recent_hires) > 0:
        first_year_rate = metrics['first_year_rate']
        st.markdown(f"""
        <div class="hr-card">
            <div class="metric-value">{first_year_rate:.1f}%</div>
            <div class="metric-label">Objectif: &lt; 20%</div>
            <progress value="{first_year_rate}" max="100" style="width:100%; height:8px; border-radius:4px;"></progress>
        </div>
        """, unsafe_allow_html=True)

# ==================== PAGE PEOPLE ====================
elif current_page == "people":
    st.markdown("""
    <div class="hr-header">
        <div class="hr-title">
            <h1>👥 Gestion des Talents</h1>
            <p>Promotions et mobilité interne</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="hr-card">
            <div class="metric-label">⭐ Promotions</div>
            <div class="metric-value">{metrics['total_promotions']}</div>
            <div>Période 2024-2025</div>
        </div>
        """, unsafe_allow_html=True)
        st.dataframe(promotions, use_container_width=True)
    
    with col2:
        st.markdown(f"""
        <div class="hr-card">
            <div class="metric-label">⏱️ Délai Promotion</div>
            <div class="metric-value">{metrics['avg_promo_delay']:.1f} ans</div>
            <div class="trend-positive">Objectif: &lt; 3 ans</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="hr-card">
            <div class="metric-label">🔄 Mobilité Interne</div>
            <div class="metric-value">{metrics['total_promotions']}</div>
            <div>Changements de poste</div>
        </div>
        """, unsafe_allow_html=True)
    
    if metrics['total_promotions'] > 0:
        promo_by_year = promotions.groupby(promotions['Promo_Date'].dt.year).size().reset_index(name='Count')
        promo_by_year.columns = ['Année', 'Nombre']
        fig = px.bar(
            promo_by_year,
            x='Année',
            y='Nombre',
            title="Évolution des Promotions",
            text='Nombre',
            color_discrete_sequence=['#2E86AB']
        )
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE MONITORING ====================
elif current_page == "monitoring":
    st.markdown("""
    <div class="hr-header">
        <div class="hr-title">
            <h1>⚠️ Système de Monitoring</h1>
            <p>Alertes et surveillance des risques</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Score de risque
    st.markdown("### 🎯 Score de Risque par Département")
    risk_df = pd.DataFrame(metrics['risk_scores'])
    st.dataframe(risk_df, use_container_width=True)
    
    fig_risk = px.bar(
        risk_df,
        x='Department',
        y='Risk_Score',
        title="Niveau de Risque par Département",
        color='Risk_Score',
        color_continuous_scale=['#10b981', '#f59e0b', '#ef4444'],
        text='Risk_Score'
    )
    fig_risk.update_traces(textposition='outside')
    st.plotly_chart(fig_risk, use_container_width=True)
    
    # Alertes
    st.markdown("### 🚨 Alertes Actives")
    
    alerts = []
    
    if metrics['turnover_rate'] > 15:
        alerts.append(("CRITICAL", f"Turnover élevé: {metrics['turnover_rate']:.1f}%", "Plan de rétention immédiat"))
    if metrics['executive_leakage'] > 10:
        alerts.append(("CRITICAL", f"Fuite des cadres: {metrics['executive_leakage']:.1f}%", "Entretiens de départ obligatoires"))
    elif metrics['executive_leakage'] > 5:
        alerts.append(("WARNING", f"Fuite des cadres: {metrics['executive_leakage']:.1f}%", "Surveillance renforcée"))
    if metrics['retention_quality'] < 80:
        alerts.append(("WARNING", f"Qualité recrutements: {metrics['retention_quality']:.1f}%", "Réviser processus d'intégration"))
    if metrics['first_year_rate'] > 20:
        alerts.append(("CRITICAL", f"Départs 1ère année: {metrics['first_year_rate']:.1f}%", "Audit du programme d'onboarding"))
    if metrics['avg_survey_rate'] < 50:
        alerts.append(("WARNING", f"Taux réponse enquêtes: {metrics['avg_survey_rate']:.1f}%", "Campagne de relance"))
    if metrics['avg_interview_rate'] < 80:
        alerts.append(("WARNING", f"Entretiens annuels: {metrics['avg_interview_rate']:.1f}%", "Planifier les entretiens manquants"))
    
    for risk in metrics['risk_scores']:
        if risk['Risk_Score'] > 15:
            alerts.append(("CRITICAL", f"Département {risk['Department']} à risque: Score {risk['Risk_Score']}", "Diagnostic approfondi"))
    
    if len(contract_alerts) > 0:
        alerts.append(("WARNING", f"{len(contract_alerts)} contrat(s) expirent dans 30 jours", "Contacter les responsables"))
    
    if alerts:
        for level, message, action in alerts:
            if level == "CRITICAL":
                st.markdown(f"""
                <div class="alert-box-critical">
                    🚨 {message}<br>
                    📋 Action recommandée: {action}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="alert-box-warning">
                    ⚠️ {message}<br>
                    📋 Action recommandée: {action}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-box-success">
            ✅ Aucune alerte critique - Tous les indicateurs sont sous contrôle
        </div>
        """, unsafe_allow_html=True)
    
    # Contrats expirant
    if len(contract_alerts) > 0:
        st.markdown("### 📄 Contrats à Échéance Proche")
        st.dataframe(contract_alerts, use_container_width=True)
    
    # Sanctions
    st.markdown("### ⚖️ Sanctions Disciplinaires")
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(sanctions, use_container_width=True)
    with col2:
        sanctions_by_dept = sanctions.groupby('Department').size().reset_index(name='Count')
        fig = px.pie(
            sanctions_by_dept,
            values='Count',
            names='Department',
            title="Sanctions par Département",
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Absentéisme
    st.markdown("### 📊 Absentéisme par Département")
    fig_abs = px.bar(
        absenteeism,
        x='Department',
        y='Absence_Rate',
        title="Taux d'Absentéisme",
        text='Absence_Rate',
        color='Absence_Rate',
        color_continuous_scale=['#10b981', '#f59e0b', '#ef4444']
    )
    fig_abs.add_hline(y=8, line_dash="dash", line_color="#ef4444", annotation_text="Seuil d'alerte 8%")
    st.plotly_chart(fig_abs, use_container_width=True)

# ==================== PAGE SETTINGS ====================
elif current_page == "settings":
    st.markdown("""
    <div class="hr-header">
        <div class="hr-title">
            <h1>⚙️ Paramètres</h1>
            <p>Configuration de l'application</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Profil utilisateur
    st.markdown("""
    <div class="config-panel">
        <div class="panel-title">👤 Profil Utilisateur</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Nom d'utilisateur", value=st.session_state.current_user, disabled=True)
        st.text_input("Email", value="contact@pratique-electronique.com")
    with col2:
        st.selectbox("Rôle", [st.session_state.user_role], disabled=True)
        lang = st.selectbox("Langue", ["Français", "English", "العربية"], index=0)
    
    # Apparence
    st.markdown("""
    <div class="config-panel">
        <div class="panel-title">🎨 Apparence</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        new_theme = st.selectbox("Thème", ["light", "dark"], index=0 if st.session_state.hr_settings["theme_mode"] == "light" else 1)
        if new_theme != st.session_state.hr_settings["theme_mode"]:
            st.session_state.hr_settings["theme_mode"] = new_theme
            st.rerun()
        
        new_color = st.color_picker("Couleur principale", st.session_state.hr_settings["accent_color"])
        st.session_state.hr_settings["accent_color"] = new_color
    with col2:
        new_font = st.selectbox("Police", ["sans-serif", "serif", "monospace"])
        st.session_state.hr_settings["font_style"] = new_font
        
        chart_h = st.slider("Hauteur des graphiques", 300, 600, st.session_state.hr_settings["chart_height"])
        st.session_state.hr_settings["chart_height"] = chart_h
    
    # Notifications
    st.markdown("""
    <div class="config-panel">
        <div class="panel-title">🔔 Notifications</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        enable_alerts = st.checkbox("Alertes turnover élevé", value=st.session_state.hr_settings["enable_alerts"])
        st.session_state.hr_settings["enable_alerts"] = enable_alerts
        
        contract_alert = st.checkbox("Alertes contrats expirant", value=st.session_state.hr_settings["contract_alerts"])
        st.session_state.hr_settings["contract_alerts"] = contract_alert
    with col2:
        auto_rep = st.checkbox("Rapport mensuel automatique", value=st.session_state.hr_settings["auto_report"])
        st.session_state.hr_settings["auto_report"] = auto_rep
        
        notify = st.checkbox("Notifications email", value=st.session_state.hr_settings["notify_email"])
        st.session_state.hr_settings["notify_email"] = notify
    
    # Base de données
    st.markdown("""
    <div class="config-panel">
        <div class="panel-title">💾 Base de Données</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        data_source = st.selectbox("Source de données", ["Fichier local (CSV)", "Excel", "SQLite", "PostgreSQL", "API REST"])
        if data_source != "Fichier local (CSV)":
            st.info("Configuration pour d'autres sources - À venir")
    
    with col2:
        refresh_mode = st.radio("Mode de mise à jour", ["Automatique", "Manuelle"], horizontal=True)
    
    # Statistiques
    st.markdown("---")
    st.markdown("### 📊 Statistiques Système")
    
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    with stat_col1:
        st.metric("Employés", len(employees))
    with stat_col2:
        st.metric("Départements", len(employees['Department'].unique()))
    with stat_col3:
        st.metric("Promotions", metrics['total_promotions'])
    with stat_col4:
        st.metric("Départs", metrics['total_exits'])
    
    # Synchronisation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Synchroniser les données", use_container_width=True):
            with st.spinner("Synchronisation en cours..."):
                time.sleep(1.5)
                st.cache_data.clear()
                employees, movements, promotions, surveys, interviews, sanctions, absenteeism, expiring_contracts = load_hr_data()
                metrics = calculate_metrics()
                st.session_state.hr_settings["last_refresh"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.success(f"✅ Synchronisation terminée - {datetime.now().strftime('%H:%M:%S')}")
                time.sleep(1)
                st.rerun()
    
    st.caption(f"📅 Dernière synchronisation: {st.session_state.hr_settings['last_refresh']}")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #64748b; font-size: 0.75rem;'>"
    "🎓 La Pratique Electronique | HR Analytics Platform | Projet PFE - Souha Ferjani | Business Intelligence"
    "</p>",
    unsafe_allow_html=True
)
