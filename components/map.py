import pydeck as pdk
import streamlit as st
import pandas as pd
from services.geo import get_coordinates

def get_color_by_risk(risk_score):
    if risk_score > 70:
        return [220, 53, 69, 200]
    elif risk_score > 30:
        return [255, 193, 7, 200]  
    else:
        return [40, 167, 69, 200]  

def render_crisis_map(df):
    if df is None or df.empty:
        st.info("ℹ️ No mappable incidents currently.")
        return

    # Filter out reports without a valid location name
    df = df[df['location'].notna() & (df['location'] != "Unknown") & (df['location'] != "")].copy()
    
    if df.empty:
        st.info("ℹ️ No reports have a known geographic location.")
        return
        
    # Get coordinates for all locations
    with st.spinner("Rendering heatmap layers..."):
        coords = df['location'].apply(get_coordinates)
        df['lat'] = coords.apply(lambda x: x[0] if x else None)
        df['lon'] = coords.apply(lambda x: x[1] if x else None)
    
    # Drop rows where geocoding failed (stability check)
    df = df.dropna(subset=['lat', 'lon']).copy()
    
    if df.empty:
        st.warning("⚠️ Could not map any of the provided locations. Please try broader filters.")
        return

    # Add color and weight columns
    df['color'] = df['risk_score'].apply(get_color_by_risk)
    df['weight'] = df['risk_score'] / 100.0  # Normalize for heatmap weight

    # Determine Map Center and Zoom
    if len(df) == 1:
        # If only 1 point, center directly on it and zoom in
        center_lat = float(df['lat'].iloc[0])
        center_lon = float(df['lon'].iloc[0])
        zoom_level = 10.0
    else:
        # Average the coordinates to find center
        center_lat = df['lat'].mean()
        center_lon = df['lon'].mean()
        # Estimate zoom based on spread
        lat_spread = df['lat'].max() - df['lat'].min()
        lon_spread = df['lon'].max() - df['lon'].min()
        max_spread = max(lat_spread, lon_spread)
        
        if max_spread < 0.5:
            zoom_level = 9.0
        elif max_spread < 2.0:
            zoom_level = 7.0
        elif max_spread < 5.0:
            zoom_level = 5.0
        else:
            zoom_level = 4.0

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=zoom_level,
        pitch=40,
    )

    # 1. Heatmap Layer
    heatmap_layer = pdk.Layer(
        "HeatmapLayer",
        data=df,
        opacity=0.6,
        get_position=["lon", "lat"],
        get_weight="weight",
        radiusPixels=50,
        colorRange=[
            [255, 255, 178],
            [254, 204, 92],
            [253, 141, 60],
            [240, 59, 32],
            [189, 0, 38]
        ]
    )

    # 2. Scatterplot Layer (Markers)
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["lon", "lat"],
        get_fill_color="color",
        get_radius=800, # meters
        pickable=True,
        opacity=0.8,
        stroked=True,
        get_line_color=[255, 255, 255],
        line_width_min_pixels=1,
    )

    # Tooltip setup
    tooltip = {
        "html": "<b>{location}</b><br/>"
                "Verdict: {verdict}<br/>"
                "Risk Score: {risk_score}<br/>"
                "<hr style='margin:5px 0;'/>"
                "<small>{input_text}</small>",
        "style": {"backgroundColor": "#1e1e1e", "color": "white", "borderRadius": "5px", "border": "1px solid #333"}
    }
    
    # Legend
    st.markdown("""
        <div style='display:flex; justify-content:flex-end; gap: 15px; margin-bottom: 5px; font-size: 13px; font-weight: 500;'>
            <div><span style='color: #dc3545;'>●</span> High Risk</div>
            <div><span style='color: #ffc107;'>●</span> Medium Risk</div>
            <div><span style='color: #28a745;'>●</span> Low Risk</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Render Map with OpenStreetMap style (no API key needed)
    deck = pdk.Deck(
        map_style="light",
        initial_view_state=view_state,
        layers=[heatmap_layer, scatter_layer],
        tooltip=tooltip
    )
    
    st.pydeck_chart(deck, use_container_width=True)
