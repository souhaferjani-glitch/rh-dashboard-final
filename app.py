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
    page_icon="<img src="https://raw.githubusercontent.com/souhaferjani-glitch/rh-dashboard-final/main/logo.png" alt="Logo">,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== LOGIN ====================
# Identifiants pour le manager RH
USERS = {
    "rhadmin": "admin2025"
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

def show_login():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        * {
            font-family: 'Inter', sans-serif;
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        .login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }
        
        .login-card {
            max-width: 450px;
            width: 100%;
            background: white;
            border-radius: 32px;
            overflow: hidden;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.3);
            animation: fadeIn 0.5s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .login-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 32px;
            text-align: center;
        }
        
        .login-logo {
            width: 80px;
            height: 80px;
            border-radius: 20px;
            margin-bottom: 16px;
            border: 3px solid rgba(255,255,255,0.3);
        }
        
        .login-title {
            font-size: 24px;
            font-weight: 700;
            color: white;
            margin-bottom: 8px;
        }
        
        .login-subtitle {
            font-size: 14px;
            color: rgba(255,255,255,0.8);
        }
        
        .login-body {
            padding: 40px;
        }
        
        .login-input {
            margin-bottom: 20px;
        }
        
        .login-input label {
            display: block;
            font-size: 13px;
            font-weight: 600;
            color: #334155;
            margin-bottom: 8px;
        }
        
        .login-input input {
            width: 100%;
            padding: 12px 16px;
            font-size: 14px;
            border: 1.5px solid #e2e8f0;
            border-radius: 12px;
            background: #fafbfc;
            transition: all 0.2s;
        }
        
        .login-input input:focus {
            border-color: #667eea;
            outline: none;
            box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
        }
        
        .login-button {
            width: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px;
            font-size: 14px;
            font-weight: 600;
            border-radius: 40px;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 20px;
        }
        
        .login-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px -5px rgba(102,126,234,0.4);
        }
        
        .login-footer {
            text-align: center;
            margin-top: 24px;
            padding-top: 20px;
            border-top: 1px solid #edf2f7;
            font-size: 11px;
            color: #94a3b8;
        }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display: none;}
    </style>
    
    <div class="login-container">
        <div class="login-card">
            <div class="login-header">
                <img src="https://raw.githubusercontent.com/souhaferjani-glitch/RH-Dashboard/main/logo.PNG" 
                     class="login-logo"
                     onerror="this.style.display='none'; this.parentElement.innerHTML='<div style=\'width:80px;height:80px;background:rgba(255,255,255,0.2);border-radius:20px;margin:0 auto 16px;display:flex;align-items:center;justify-content:center\'><span style=\'font-size:40px;color:white\'>📊</span></div>'">
                <div class="login-title">RH Dashboard</div>
                <div class="login-subtitle">La Pratique Electronique</div>
            </div>
 
