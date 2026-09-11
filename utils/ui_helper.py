# -*- coding: utf-8 -*-
"""
UI Styles and Themes Helper Module
Injects custom CSS headers into pages to maintain visual branding and style consistency.
"""

from pathlib import Path
import streamlit as st

def apply_custom_themee():
    """Apply custom theme here"""

def apply_custom_theme():
    """
    Apply a fresh greenish-toned UI theme to the main app.
    """
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #f7fff8 0%, #eefbf2 100%);
            color: #153522;
        }

        h1, h2, h3, h4 {
            font-family: 'Inter', -apple-system, sans-serif !important;
            font-weight: 700 !important;
            color: #166534 !important;
             
            letter-spacing: -0.02em;
        }

        div[data-testid="stMetricValue"] {
            font-size: 2rem !important;
            font-weight: 700 !important;
            color: #15803d !important;
            font-family: 'JetBrains Mono', monospace !important;
        }

        div[data-testid="stMetricLabel"] {
            color: #4b5563 !important;
            font-size: 0.8rem !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .terminal-card {
            background: linear-gradient(145deg, #ffffff 0%, #f3fef6 100%);
            border: 1px solid #bbf7d0;
            border-radius: 14px;
            padding: 1.1rem;
            margin-bottom: 1rem;
            box-shadow: 0 8px 24px rgba(21, 128, 61, 0.08);
        }

        .status-badge-active {
            background-color: #dcfce7;
            color: #166534;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
            border: 1px solid #86efac;
            display: inline-block;
        }

        .status-badge-alert {
            background-color: #fef2f2;
            color: #b91c1c;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
            border: 1px solid #fecaca;
            display: inline-block;
        }

        .stButton>button {
            background: linear-gradient(135deg, #16a34a 0%, #22c55e 100%) !important;
            color: #ffffff !important;
            border-radius: 10px !important;
            border: none !important;
            padding: 0.45rem 1.2rem !important;
            font-weight: 700 !important;
            transition: all 0.2s ease-in-out;
            box-shadow: 0 4px 12px rgba(22, 163, 74, 0.2);
        }

        .stButton>button:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(22, 163, 74, 0.25);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f7fff9 0%, #eefbf1 100%) !important;
            border-right: 1px solid #bbf7d0;
        }

        [data-testid="stForm"] {
            background: #ffffff !important;
            border: 1px solid #d1fae5 !important;
            border-radius: 14px !important;
            padding: 1.2rem !important;
            box-shadow: 0 6px 16px rgba(21, 128, 61, 0.06);
        }

        input[type="text"], input[type="email"], textarea, select {
            background-color: #ffffff !important;
            color: #14532d !important;
            border: 1px solid #86efac !important;
            border-radius: 8px !important;
        }
    </style>
    """, unsafe_allow_html=True)

def render_sidebar_header():
    """Renders a elegant system header in the sidebar."""
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        display: flex;
        flex-direction: column;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
        order: 2;
        margin-top: 0.25rem;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarContent"] > div:first-child {
        order: 1;
    }
    </style>
    """, unsafe_allow_html=True)

    logo_path = Path(__file__).resolve().parent.parent / "data" / "Images" / "Rail Face.png"
    if logo_path.exists():
        st.sidebar.image(str(logo_path), width=120)

    st.sidebar.markdown("""
        <div style='text-align: center; padding: 0.2rem 0 0.4rem 0;'>
            <h2 style='margin-bottom: 0px; font-size: 1.1rem;'>RAILWAY FACE REC Pro</h2>
            <p style='color: #64748b; font-size: 0.8rem; margin-top: 4px;'>AI Node Started</p>
        </div>
        <hr style="border-top: 1px solid #1e293b; margin: 0.2rem 0 0.6rem 0;"/>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown(""" 
        <div style='padding: 12px; border-radius: 8px; background-color: #111827; border: 1px solid #1e293b; margin-top: 0.2rem;'>
            <p style='margin-bottom: 2px; font-size: 0.7rem; color: #94a3b8; letter-spacing: 0.05em;'>🛡️ ACTIVE NODE SHIELD</p>
            <p style='margin-bottom: 0px; font-size: 0.85rem; color: #10b981; font-weight: bold;'>● STREAM STATUS: LIVE</p>
            <p style='margin-top: 6px; font-size: 0.7rem; color: #64748b;'>Terminal ID: NODE-3000</p>
        </div>
    """, unsafe_allow_html=True)
