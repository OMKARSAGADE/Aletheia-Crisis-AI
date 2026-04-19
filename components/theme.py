import streamlit as st

def apply_premium_theme():
    st.markdown("""
    <style>
    /* Global Base Settings (Clean Light Theme) */
    :root {
        --bg-color: #ffffff;
        --card-bg: #ffffff;
        --primary-accent: #ff4b4b; /* Streamlit default red/pink */
        --secondary-accent: #0068c9;
        --text-main: #31333f;
        --text-muted: #6e7589;
        --danger: #ff4b4b;
        --success: #21c354;
        --warning: #ffc107;
        --sidebar-bg: #f0f2f6;
        --border-color: #e6e9ef;
    }

    /* Main Background */
    .stApp {
        background-color: var(--bg-color);
        color: var(--text-main);
        font-family: 'Source Sans Pro', sans-serif;
    }

    /* Top Padding and Headers */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-main) !important;
        font-weight: 600 !important;
    }
    
    h1 {
        margin-bottom: 1.5rem !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border-color);
    }
    
    /* Aletheia Header Injection */
    [data-testid="stSidebarNav"]::before {
        content: "Aletheia";
        display: block;
        padding: 1.5rem 1.5rem 1rem 1.5rem;
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--secondary-accent);
        letter-spacing: 0.5px;
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 0.5rem;
    }

    /* Capitalize Sidebar Navigation Items & Headers */
    [data-testid="stSidebarNav"] span {
        text-transform: capitalize !important;
        font-weight: 500 !important;
    }
    
    /* Better spacing and active item highlight */
    [data-testid="stSidebarNav"] ul li a {
        padding-top: 0.25rem;
        padding-bottom: 0.25rem;
    }
    [data-testid="stSidebarNav"] [data-testid="stSidebarNavLink"] {
        transition: all 0.2s ease;
    }
    [data-testid="stSidebarNav"] [data-testid="stSidebarNavLink"]:hover {
        background-color: rgba(0, 104, 201, 0.05) !important;
        border-radius: 6px;
    }
    
    /* Metrics and Cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: var(--text-main) !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        color: var(--text-muted) !important;
    }
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > textarea {
        background-color: #ffffff !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-main) !important;
        border-radius: 4px !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > textarea:focus {
        border-color: var(--primary-accent) !important;
        box-shadow: 0 0 0 1px var(--primary-accent) !important;
    }

    /* Dataframes/Tables */
    .stDataFrame {
        background-color: transparent !important;
    }
    [data-testid="stTable"] {
        background-color: var(--card-bg) !important;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Dividers */
    hr {
        border-color: var(--border-color) !important;
        margin: 2rem 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)
