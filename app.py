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

# Configuration de la page
st.set_page_config(
    page_title="RH Analytics Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== INITIALISATION DE LA SESSION ====================
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.auth_status = False
    st.session_state.user_data = {}
    st.session_state.preferences = {
        'theme': 'light',
        'accent_color': '#FF6B35',
        'notifications': True,
        'auto_refresh': False,
        'dashboard_layout': 'compact'
    }
    st.session_state.data_cache = {}
    st.session_state.last_refresh = datetime.now()

# ==================== GESTION DES DONNÉES ====================
class DataManager:
    """Classe pour la gestion centralisée des données"""
    
    @staticmethod
    @st.cache_data(ttl=300)
    def load_all_data():
        """Charge toutes les données nécessaires"""
        
        # Données des employés
        employees = pd.DataFrame({
            'ID': ['E001','E002','E003','E004','E005','E006','E007','E008','E009','E010',
                   'E011','E012','E013','E014','E015','E016','E017','E018','E019','E020'],
            'Hire_Date': pd.date_range('2020-01-01', periods=20, freq='ME'),
            'Exit_Date': [pd.NaT] * 20,
            'Exit_Reason': [''] * 20,
            'Department': np.random.choice(['Sales', 'Engineering', 'HR', 'Marketing', 'Finance'], 20),
            'Level': np.random.choice(['Junior', 'Senior', 'Manager', 'Director'], 20, p=[0.4, 0.35, 0.2, 0.05]),
            'Gender': np.random.choice(['M', 'F'], 20, p=[0.55, 0.45]),
            'Age': np.random.randint(22, 60, 20),
            'Salary': np.random.randint(30000, 120000, 20),
            'Performance_Score': np.random.uniform(2, 5, 20).round(1)
        })
        
        # Ajouter quelques départs
        exit_indices = [2, 7, 12, 15]
        exit_reasons = ['Resignation', 'Retirement', 'Termination', 'Resignation']
        for idx, reason in zip(exit_indices, exit_reasons):
            employees.loc[idx, 'Exit_Date'] = pd.Timestamp('2024-12-01')
            employees.loc[idx, 'Exit_Reason'] = reason
        
        # Données des mouvements mensuels
        movements = pd.DataFrame({
            'Month': pd.date_range('2024-01-01', periods=12, freq='ME'),
            'Hires': np.random.poisson(2, 12),
            'Resignations': np.random.poisson(1, 12),
            'Retirements': np.random.poisson(0.3, 12).astype(int),
            'Terminations': np.random.poisson(0.5, 12).astype(int)
        })
        
        # Données des promotions
        promotions = pd.DataFrame({
            'Employee_ID': ['E001', 'E003', 'E008', 'E011', 'E014', 'E018'],
            'Promotion_Date': pd.date_range('2024-01-15', periods=6, freq='ME'),
            'Old_Title': ['Sales Rep', 'Engineer', 'HR Assistant', 'Marketing Coord', 'Financial Analyst', 'Tech Lead'],
            'New_Title': ['Sales Manager', 'Senior Engineer', 'HR Manager', 'Marketing Manager', 'Finance Manager', 'Director'],
            'Salary_Increase': np.random.uniform(0.08, 0.25, 6)
        })
        
        # Données des enquêtes
        surveys = pd.DataFrame({
            'Period': pd.date_range('2024-01-01', periods=12, freq='ME').strftime('%b %Y'),
            'Sent': [50] * 12,
            'Responses': np.random.randint(30, 48, 12),
            'Engagement_Score': np.random.uniform(65, 92, 12).round(1)
        })
        surveys['Response_Rate'] = (surveys['Responses'] / surveys['Sent'] * 100).round(1)
        
        # Données des entretiens
        interviews = pd.DataFrame({
            'Year': [2022, 2023, 2024],
            'Scheduled': [18, 22, 25],
            'Completed': [15, 19, 21],
            'Completion_Rate': [83.3, 86.4, 84.0]
        })
        
        # Données disciplinaires
        disciplines = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=15, freq='W'),
            'Department': np.random.choice(['Sales', 'Engineering', 'HR', 'Marketing', 'Finance'], 15),
            'Type': np.random.choice(['Warning', 'Suspension', 'Termination'], 15, p=[0.7, 0.2, 0.1]),
            'Employee_ID': np.random.choice(['E001', 'E002', 'E003', 'E004', 'E005'], 15)
        })
        
        # Données d'absentéisme
        absenteeism = pd.DataFrame({
            'Month': pd.date_range('2024-01-01', periods=12, freq='ME').strftime('%b %Y'),
            'Department': np.repeat(['Sales', 'Engineering', 'HR', 'Marketing', 'Finance'], 12),
            'Absence_Rate': np.random.uniform(2, 12, 60).round(1)
        })
        
        # Contrats expirant
        expiring_contracts = pd.DataFrame({
            'Employee_ID': ['E009', 'E013', 'E016', 'E019'],
            'End_Date': pd.to_datetime(['2026-04-15', '2026-04-25', '2026-05-10', '2026-05-20']),
            'Contract_Type': ['CDD', 'CDD', 'CDD', 'CDD'],
            'Department': ['Engineering', 'Sales', 'Marketing', 'Finance']
        })
        
        return {
            'employees': employees,
            'movements': movements,
            'promotions': promotions,
            'surveys': surveys,
            'interviews': interviews,
            'disciplines': disciplines,
            'absenteeism': absenteeism,
            'expiring_contracts': expiring_contracts
        }
    
    @staticmethod
    def calculate_metrics(data):
        """Calcule tous les indicateurs clés"""
        
        employees = data['employees']
        movements = data['movements']
        surveys = data['surveys']
        interviews = data['interviews']
        promotions = data['promotions']
        
        active = employees[employees['Exit_Date'].isna()]
        total_active = len(active)
        total_employees = len(employees)
        departures = employees['Exit_Date'].notna().sum()
        
        # Turnover rate
        turnover_rate = (departures / total_employees * 100) if total_employees > 0 else 0
        
        # Cadres (niveau Manager et Director)
        executives = active[active['Level'].isin(['Manager', 'Director'])]
        executive_count = len(executives)
        executive_turnover = employees[(employees['Level'].isin(['Manager', 'Director'])) & 
                                        (employees['Exit_Date'].notna())].shape[0]
        executive_turnover_rate = (executive_turnover / (executive_count + executive_turnover) * 100) if (executive_count + executive_turnover) > 0 else 0
        
        # Qualité des recrutements (employés récents toujours actifs)
        recent_hires = employees[employees['Hire_Date'] > datetime.now() - timedelta(days=365)]
        retention_quality = (recent_hires[recent_hires['Exit_Date'].isna()].shape[0] / len(recent_hires) * 100) if len(recent_hires) > 0 else 0
        
        # Taux de réponse moyen
        avg_response_rate = surveys['Response_Rate'].mean()
        
        # Taux d'entretiens
        avg_interview_rate = interviews['Completion_Rate'].mean()
        
        # Délai moyen de promotion
        promo_employees = promotions.merge(employees[['ID', 'Hire_Date']], left_on='Employee_ID', right_on='ID')
        promo_employees['Time_to_Promotion'] = (promo_employees['Promotion_Date'] - promo_employees['Hire_Date']).dt.days / 365.25
        avg_promotion_delay = promo_employees['Time_to_Promotion'].mean() if len(promo_employees) > 0 else 0
        
        # Turnover par département
        dept_turnover = []
        for dept in employees['Department'].unique():
            dept_total = employees[employees['Department'] == dept].shape[0]
            dept_exits = employees[(employees['Department'] == dept) & (employees['Exit_Date'].notna())].shape[0]
            dept_rate = (dept_exits / dept_total * 100) if dept_total > 0 else 0
            dept_turnover.append({'Department': dept, 'Turnover_Rate': round(dept_rate, 1), 'Exits': dept_exits, 'Total': dept_total})
        
        return {
            'total_active': total_active,
            'total_employees': total_employees,
            'departures': departures,
            'turnover_rate': turnover_rate,
            'executive_count': executive_count,
            'executive_turnover_rate': executive_turnover_rate,
            'retention_quality': retention_quality,
            'avg_response_rate': avg_response_rate,
            'avg_interview_rate': avg_interview_rate,
            'avg_promotion_delay': avg_promotion_delay,
            'dept_turnover': pd.DataFrame(dept_turnover),
            'total_promotions': len(promotions)
        }

# ==================== AUTHENTIFICATION ====================
def show_auth_page():
    """Page d'authentification moderne"""
    
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    .auth-container {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        position: relative;
        overflow: hidden;
    }
    
    .auth-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 2rem;
        padding: 3rem;
        width: 100%;
        max-width: 450px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        animation: slideUp 0.5s ease-out;
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .auth-logo {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .auth-logo-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    .auth-title {
        font-size: 1.875rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .auth-subtitle {
        text-align: center;
        color: #6b7280;
        font-size: 0.875rem;
        margin-bottom: 2rem;
    }
    
    .stTextInput > div > div > input {
        border-radius: 0.75rem;
        border: 1.5px solid #e5e7eb;
        padding: 0.75rem 1rem;
        font-size: 0.875rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        border-radius: 0.75rem;
        font-weight: 600;
        font-size: 0.875rem;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px -10px rgba(102, 126, 234, 0.5);
    }
    
    .auth-footer {
        text-align: center;
        margin-top: 1.5rem;
        font-size: 0.75rem;
        color: #9ca3af;
    }
    </style>
    
    <div class="auth-container">
        <div class="auth-card">
            <div class="auth-logo">
                <div class="auth-logo-icon">🎯</div>
                <div class="auth-title">RH Analytics</div>
                <div class="auth-subtitle">Plateforme de pilotage RH</div>
            </div>
    """, unsafe_allow_html=True)
    
    username = st.text_input("Identifiant", placeholder="admin@rh.com", key="auth_user")
    password = st.text_input("Mot de passe", type="password", placeholder="••••••••", key="auth_pass")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔐 Se connecter", use_container_width=True):
            if username == "admin@rh.com" and password == "admin123":
                st.session_state.auth_status = True
                st.session_state.user_data = {'name': 'Administrateur', 'role': 'admin', 'email': username}
                st.rerun()
            else:
                st.error("❌ Identifiants invalides")
    
    st.markdown("""
            <div class="auth-footer">
                <p>© 2024 RH Analytics - Tous droits réservés</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==================== COMPOSANTS UI RÉUTILISABLES ====================
class UIComponents:
    """Composants d'interface réutilisables"""
    
    @staticmethod
    def metric_card(title, value, trend=None, icon="📊", color="#FF6B35"):
        """Carte métrique stylisée"""
        
        trend_html = ""
        if trend:
            trend_class = "trend-up" if trend > 0 else "trend-down"
            trend_symbol = "▲" if trend > 0 else "▼"
            trend_html = f'<div class="{trend_class}">{trend_symbol} {abs(trend)}%</div>'
        
        return f"""
        <div class="metric-card" style="border-top: 4px solid {color};">
            <div class="metric-icon">{icon}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-title">{title}</div>
            {trend_html}
        </div>
        """
    
    @staticmethod
    def alert_banner(type_, message, action=None):
        """Bannière d'alerte"""
        
        colors = {
            'critical': {'bg': '#FEE2E2', 'border': '#EF4444', 'icon': '🔴'},
            'warning': {'bg': '#FEF3C7', 'border': '#F59E0B', 'icon': '⚠️'},
            'success': {'bg': '#D1FAE5', 'border': '#10B981', 'icon': '✅'},
            'info': {'bg': '#DBEAFE', 'border': '#3B82F6', 'icon': 'ℹ️'}
        }
        
        color = colors.get(type_, colors['info'])
        
        action_html = f'<div class="alert-action">{action}</div>' if action else ''
        
        return f"""
        <div class="alert-banner" style="background: {color['bg']}; border-left-color: {color['border']};">
            <div class="alert-icon">{color['icon']}</div>
            <div class="alert-message">{message}</div>
            {action_html}
        </div>
        """
    
    @staticmethod
    def stat_grid(stats_data):
        """Grille de statistiques"""
        
        cols = st.columns(len(stats_data))
        for col, stat in zip(cols, stats_data):
            with col:
                st.markdown(UIComponents.metric_card(
                    stat['title'], 
                    stat['value'], 
                    stat.get('trend'),
                    stat.get('icon', '📊'),
                    stat.get('color', '#FF6B35')
                ), unsafe_allow_html=True)

# ==================== STYLES CSS ====================
def load_styles():
    """Charge les styles CSS dynamiques"""
    
    accent_color = st.session_state.preferences.get('accent_color', '#FF6B35')
    theme = st.session_state.preferences.get('theme', 'light')
    
    bg_color = '#F9FAFB' if theme == 'light' else '#111827'
    card_bg = '#FFFFFF' if theme == 'light' else '#1F2937'
    text_color = '#111827' if theme == 'light' else '#F9FAFB'
    text_secondary = '#6B7280' if theme == 'light' else '#9CA3AF'
    
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {{
        font-family: 'Inter', sans-serif;
    }}
    
    .stApp {{
        background: {bg_color};
    }}
    
    /* Cartes métriques */
    .metric-card {{
        background: {card_bg};
        border-radius: 1rem;
        padding: 1.25rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: all 0.3s;
        margin: 0.5rem 0;
    }}
    
    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1);
    }}
    
    .metric-icon {{
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }}
    
    .metric-value {{
        font-size: 2rem;
        font-weight: 800;
        color: {text_color};
        margin: 0.25rem 0;
    }}
    
    .metric-title {{
        font-size: 0.75rem;
        color: {text_secondary};
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    
    .trend-up {{
        color: #10B981;
        font-size: 0.7rem;
        margin-top: 0.5rem;
    }}
    
    .trend-down {{
        color: #EF4444;
        font-size: 0.7rem;
        margin-top: 0.5rem;
    }}
    
    /* Alertes */
    .alert-banner {{
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem;
        border-radius: 0.75rem;
        border-left-width: 4px;
        border-left-style: solid;
        margin: 0.5rem 0;
    }}
    
    .alert-icon {{
        font-size: 1.25rem;
    }}
    
    .alert-message {{
        flex: 1;
        font-weight: 500;
    }}
    
    .alert-action {{
        font-size: 0.75rem;
        color: {accent_color};
        font-weight: 600;
    }}
    
    /* En-têtes */
    .dashboard-header {{
        background: linear-gradient(135deg, {accent_color}20 0%, {accent_color}05 100%);
        border-radius: 1rem;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }}
    
    .dashboard-title {{
        font-size: 1.5rem;
        font-weight: 700;
        color: {text_color};
        margin-bottom: 0.25rem;
    }}
    
    .dashboard-subtitle {{
        color: {text_secondary};
        font-size: 0.875rem;
    }}
    
    /* Sections */
    .section-card {{
        background: {card_bg};
        border-radius: 1rem;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }}
    
    .section-title {{
        font-size: 1.125rem;
        font-weight: 600;
        color: {text_color};
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid {accent_color};
        display: inline-block;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: {card_bg};
        border-right: 1px solid {text_secondary}20;
    }}
    
    /* Boutons */
    .stButton > button {{
        background: {accent_color};
        color: white;
        border: none;
        border-radius: 0.5rem;
        transition: all 0.3s;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 5px 15px {accent_color}40;
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.5rem;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: {card_bg};
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
    }}
    </style>
    """, unsafe_allow_html=True)

# ==================== DASHBOARD PRINCIPAL ====================
def render_dashboard():
    """Affiche le dashboard principal"""
    
    # Chargement des données
    data = DataManager.load_all_data()
    metrics = DataManager.calculate_metrics(data)
    
    # En-tête
    st.markdown(f"""
    <div class="dashboard-header">
        <div class="dashboard-title">🎯 RH Analytics Dashboard</div>
        <div class="dashboard-subtitle">Tableau de bord stratégique - Mise à jour {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # KPIs principaux
    kpi_cols = st.columns(5)
    
    with kpi_cols[0]:
        st.markdown(UIComponents.metric_card(
            "Effectif Total",
            f"{metrics['total_active']}",
            icon="👥",
            color=st.session_state.preferences['accent_color']
        ), unsafe_allow_html=True)
    
    with kpi_cols[1]:
        st.markdown(UIComponents.metric_card(
            "Turnover",
            f"{metrics['turnover_rate']:.1f}%",
            icon="🔄",
            color=st.session_state.preferences['accent_color']
        ), unsafe_allow_html=True)
    
    with kpi_cols[2]:
        st.markdown(UIComponents.metric_card(
            "Cadres",
            f"{metrics['executive_count']}",
            icon="⭐",
            color=st.session_state.preferences['accent_color']
        ), unsafe_allow_html=True)
    
    with kpi_cols[3]:
        st.markdown(UIComponents.metric_card(
            "Promotions",
            f"{metrics['total_promotions']}",
            icon="📈",
            color=st.session_state.preferences['accent_color']
        ), unsafe_allow_html=True)
    
    with kpi_cols[4]:
        st.markdown(UIComponents.metric_card(
            "Départs",
            f"{metrics['departures']}",
            icon="🚪",
            color=st.session_state.preferences['accent_color']
        ), unsafe_allow_html=True)
    
    # Alertes automatiques
    alerts = []
    
    if metrics['turnover_rate'] > 15:
        alerts.append(('critical', f"Turnover élevé: {metrics['turnover_rate']:.1f}%", "Plan de rétention urgent"))
    
    if metrics['executive_turnover_rate'] > 10:
        alerts.append(('warning', f"Turnover des cadres: {metrics['executive_turnover_rate']:.1f}%", "Audit des départs cadres"))
    
    if metrics['retention_quality'] < 80:
        alerts.append(('warning', f"Qualité recrutement: {metrics['retention_quality']:.1f}%", "Revue processus onboarding"))
    
    if metrics['avg_response_rate'] < 50:
        alerts.append(('warning', f"Participation enquêtes: {metrics['avg_response_rate']:.1f}%", "Campagne de relance"))
    
    # Contrats expirants
    expiring = data['expiring_contracts']
    expiring_soon = expiring[expiring['End_Date'] <= datetime.now() + timedelta(days=30)]
    if len(expiring_soon) > 0:
        alerts.append(('critical', f"{len(expiring_soon)} contrat(s) expirent dans 30 jours", "Contacter les responsables"))
    
    # Affichage des alertes
    if alerts:
        st.markdown("### 🚨 Alertes et Recommandations")
        for alert_type, message, action in alerts:
            st.markdown(UIComponents.alert_banner(alert_type, message, action), unsafe_allow_html=True)
    
    # Onglets principaux
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Vue d'ensemble", "👥 Personnel", "📈 Performances", "⚙️ Administration"])
    
    with tab1:
        # Graphiques de synthèse
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🏢 Répartition par département</div>', unsafe_allow_html=True)
            
            dept_dist = data['employees'][data['employees']['Exit_Date'].isna()]['Department'].value_counts()
            fig = px.pie(values=dept_dist.values, names=dept_dist.index, 
                         hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(showlegend=True, height=400, margin=dict(t=0, l=0, r=0, b=0))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">📈 Évolution mensuelle</div>', unsafe_allow_html=True)
            
            movements = data['movements']
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=movements['Month'], y=movements['Hires'].cumsum(),
                                     name='Entrées cumulées', fill='tozeroy', line=dict(color='#10B981', width=2)))
            fig.add_trace(go.Scatter(x=movements['Month'], y=movements['Resignations'].cumsum(),
                                     name='Sorties cumulées', fill='tozeroy', line=dict(color='#EF4444', width=2)))
            fig.update_layout(height=400, margin=dict(t=0, l=0, r=0, b=0))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Turnover par département
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🔄 Turnover par département</div>', unsafe_allow_html=True)
        
        fig = px.bar(metrics['dept_turnover'], x='Department', y='Turnover_Rate',
                     text='Turnover_Rate', color='Turnover_Rate',
                     color_continuous_scale=['#10B981', '#F59E0B', '#EF4444'])
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(height=400, xaxis_title="", yaxis_title="Taux de turnover (%)")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">👥 Distribution par niveau</div>', unsafe_allow_html=True)
            
            level_dist = data['employees'][data['employees']['Exit_Date'].isna()]['Level'].value_counts()
            fig = px.bar(x=level_dist.index, y=level_dist.values, text=level_dist.values,
                         color=level_dist.index, color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(showlegend=False, height=350, xaxis_title="", yaxis_title="Nombre")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">⚧️ Parité Homme/Femme</div>', unsafe_allow_html=True)
            
            gender_dist = data['employees'][data['employees']['Exit_Date'].isna()]['Gender'].value_counts()
            fig = px.pie(values=gender_dist.values, names=gender_dist.index,
                         hole=0.3, color_discrete_sequence=['#3B82F6', '#EC4899'])
            fig.update_layout(height=350, margin=dict(t=0, l=0, r=0, b=0))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Liste des employés
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📋 Liste des employés actifs</div>', unsafe_allow_html=True)
        
        active_employees = data['employees'][data['employees']['Exit_Date'].isna()].copy()
        active_employees_display = active_employees[['ID', 'Department', 'Level', 'Gender', 'Age', 'Performance_Score']].head(10)
        st.dataframe(active_employees_display, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">⭐ Évolution des promotions</div>', unsafe_allow_html=True)
            
            promotions_by_month = data['promotions'].groupby(data['promotions']['Promotion_Date'].dt.strftime('%b %Y')).size()
            fig = px.line(x=promotions_by_month.index, y=promotions_by_month.values,
                          markers=True, line_shape='spline')
            fig.update_layout(height=350, xaxis_title="", yaxis_title="Nombre de promotions")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">⏱️ Délai moyen de promotion</div>', unsafe_allow_html=True)
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=metrics['avg_promotion_delay'],
                title={'text': "Années"},
                gauge={'axis': {'range': [0, 8]},
                       'bar': {'color': st.session_state.preferences['accent_color']},
                       'steps': [
                           {'range': [0, 2], 'color': '#D1FAE5'},
                           {'range': [2, 4], 'color': '#FEF3C7'},
                           {'range': [4, 8], 'color': '#FEE2E2'}
                       ]}
            ))
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Enquêtes et entretiens
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 Participation aux enquêtes</div>', unsafe_allow_html=True)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=data['surveys']['Period'], y=data['surveys']['Sent'],
                             name='Diffusés', marker_color='#94A3B8'))
        fig.add_trace(go.Bar(x=data['surveys']['Period'], y=data['surveys']['Responses'],
                             name='Réponses', marker_color=st.session_state.preferences['accent_color']))
        fig.update_layout(barmode='group', height=400, xaxis_title="", yaxis_title="Nombre")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Taux de réponse
        fig = px.line(data['surveys'], x='Period', y='Response_Rate',
                      markers=True, line_shape='spline')
        fig.add_hline(y=75, line_dash="dash", line_color="#10B981", annotation_text="Objectif")
        fig.add_hline(y=50, line_dash="dash", line_color="#EF4444", annotation_text="Seuil critique")
        fig.update_layout(height=350, yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">⚖️ Sanctions disciplinaires</div>', unsafe_allow_html=True)
            
            sanctions_by_dept = data['disciplines'].groupby('Department').size().reset_index(name='Count')
            fig = px.bar(sanctions_by_dept, x='Department', y='Count', text='Count',
                         color='Count', color_continuous_scale='Oranges')
            fig.update_layout(height=350, xaxis_title="", yaxis_title="Nombre de sanctions")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">📋 Entretiens annuels</div>', unsafe_allow_html=True)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(x=data['interviews']['Year'], y=data['interviews']['Scheduled'],
                                 name='Planifiés', marker_color='#94A3B8'))
            fig.add_trace(go.Bar(x=data['interviews']['Year'], y=data['interviews']['Completed'],
                                 name='Réalisés', marker_color=st.session_state.preferences['accent_color']))
            fig.update_layout(barmode='group', height=350, xaxis_title="", yaxis_title="Nombre")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Absentéisme
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 Absentéisme par département</div>', unsafe_allow_html=True)
        
        avg_absence = data['absenteeism'].groupby('Department')['Absence_Rate'].mean().reset_index()
        fig = px.bar(avg_absence, x='Department', y='Absence_Rate', text='Absence_Rate',
                     color='Absence_Rate', color_continuous_scale='Reds')
        fig.add_hline(y=8, line_dash="dash", line_color="#EF4444", annotation_text="Seuil d'alerte")
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(height=400, xaxis_title="", yaxis_title="Taux d'absentéisme (%)")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Contrats expirant
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📄 Contrats arrivant à expiration</div>', unsafe_allow_html=True)
        
        expiring_contracts = data['expiring_contracts']
        expiring_contracts['Days_Left'] = (expiring_contracts['End_Date'] - datetime.now()).dt.days
        expiring_contracts['Status'] = expiring_contracts['Days_Left'].apply(
            lambda x: '🔴 Urgent' if x <= 30 else '🟡 Proche' if x <= 60 else '🟢 Normal'
        )
        st.dataframe(expiring_contracts[['Employee_ID', 'Department', 'End_Date', 'Days_Left', 'Status']], 
                    use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ==================== SIDEBAR ====================
def render_sidebar():
    """Affiche la barre latérale"""
    
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <div style="font-size: 3rem;">🎯</div>
            <h3 style="margin: 0.5rem 0 0 0;">RH Analytics</h3>
            <p style="font-size: 0.7rem; opacity: 0.7;">v2.0 - Business Intelligence</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Informations utilisateur
        if st.session_state.user_data:
            st.markdown(f"""
            <div style="padding: 0.5rem; background: rgba(255,255,255,0.05); border-radius: 0.5rem; margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <div style="font-size: 2rem;">👤</div>
                    <div>
                        <div style="font-weight: 600;">{st.session_state.user_data.get('name', 'Utilisateur')}</div>
                        <div style="font-size: 0.7rem; opacity: 0.7;">{st.session_state.user_data.get('role', 'user')}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Navigation rapide
        st.markdown("### 📍 Navigation")
        quick_links = {
            "🏠 Accueil": "overview",
            "👥 Personnel": "employees",
            "📈 Analytics": "analytics",
            "⚙️ Paramètres": "settings"
        }
        
        for label, key in quick_links.items():
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.current_page = key
        
        st.markdown("---")
        
        # Filtres
        st.markdown("### 🔍 Filtres")
        
        data = DataManager.load_all_data()
        departments = ['Tous'] + list(data['employees']['Department'].unique())
        selected_dept = st.selectbox("Département", departments, key="filter_dept")
        
        levels = ['Tous'] + list(data['employees']['Level'].unique())
        selected_level = st.selectbox("Niveau", levels, key="filter_level")
        
        st.markdown("---")
        
        # Export
        st.markdown("### 📎 Actions")
        
        if st.button("📥 Exporter rapport PDF", use_container_width=True):
            st.info("Fonctionnalité à venir")
        
        if st.button("📧 Envoyer par email", use_container_width=True):
            st.info("Fonctionnalité à venir")
        
        st.markdown("---")
        
        # Déconnexion
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state.auth_status = False
            st.session_state.user_data = {}
            st.rerun()
        
        st.markdown("---")
        st.caption("© 2024 RH Analytics")
        st.caption("Tous droits réservés")

# ==================== PAGE PARAMÈTRES ====================
def render_settings():
    """Affiche la page des paramètres"""
    
    st.markdown("""
    <div class="dashboard-header">
        <div class="dashboard-title">⚙️ Paramètres et Configuration</div>
        <div class="dashboard-subtitle">Personnalisez votre expérience</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🎨 Apparence</div>', unsafe_allow_html=True)
        
        # Thème
        theme = st.selectbox(
            "Thème",
            ["Clair", "Sombre"],
            index=0 if st.session_state.preferences['theme'] == 'light' else 1
        )
        st.session_state.preferences['theme'] = 'light' if theme == 'Clair' else 'dark'
        
        # Couleur d'accent
        accent_color = st.color_picker(
            "Couleur principale",
            st.session_state.preferences['accent_color']
        )
        st.session_state.preferences['accent_color'] = accent_color
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🔔 Notifications</div>', unsafe_allow_html=True)
        
        st.session_state.preferences['notifications'] = st.checkbox(
            "Activer les notifications",
            st.session_state.preferences['notifications']
        )
        
        st.session_state.preferences['auto_refresh'] = st.checkbox(
            "Actualisation automatique",
            st.session_state.preferences['auto_refresh']
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 Affichage</div>', unsafe_allow_html=True)
        
        layout = st.selectbox(
            "Disposition du dashboard",
            ["Compact", "Confortable", "Large"],
            index=["Compact", "Confortable", "Large"].index(
                st.session_state.preferences.get('dashboard_layout', 'Compact')
            )
        )
        st.session_state.preferences['dashboard_layout'] = layout.lower()
        
        charts_per_row = st.slider("Graphiques par ligne", 1, 4, 2)
        st.session_state.preferences['charts_per_row'] = charts_per_row
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">💾 Données</div>', unsafe_allow_html=True)
        
        if st.button("🔄 Rafraîchir les données", use_container_width=True):
            st.cache_data.clear()
            st.success("✅ Données rafraîchies avec succès!")
            time.sleep(1)
            st.rerun()
        
        st.caption(f"Dernière mise à jour: {st.session_state.last_refresh.strftime('%d/%m/%Y %H:%M:%S')}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Réinitialisation
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚠️ Zone dangereuse</div>', unsafe_allow_html=True)
    
    if st.button("🔄 Réinitialiser tous les paramètres", use_container_width=True):
        st.session_state.preferences = {
            'theme': 'light',
            'accent_color': '#FF6B35',
            'notifications': True,
            'auto_refresh': False,
            'dashboard_layout': 'compact'
        }
        st.success("✅ Paramètres réinitialisés!")
        time.sleep(1)
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== POINT D'ENTRÉE PRINCIPAL ====================
def main():
    """Point d'entrée principal de l'application"""
    
    # Chargement des styles
    load_styles()
    
    # Vérification de l'authentification
    if not st.session_state.auth_status:
        show_auth_page()
        return
    
    # Sidebar
    render_sidebar()
    
    # Contenu principal
    if not hasattr(st.session_state, 'current_page') or st.session_state.current_page == 'overview':
        render_dashboard()
    elif st.session_state.current_page == 'settings':
        render_settings()
    else:
        render_dashboard()

if __name__ == "__main__":
    main()
