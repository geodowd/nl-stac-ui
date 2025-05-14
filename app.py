import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide", page_title="STAC Query Explorer")

# --- Session State Initialization ---
if "metadata" not in st.session_state:
    st.session_state["metadata"] = None
if "features" not in st.session_state:
    st.session_state["features"] = []
if "result_ids" not in st.session_state:
    st.session_state["result_ids"] = []
if "selected_id" not in st.session_state:
    st.session_state["selected_id"] = None
if "last_bounds" not in st.session_state:
    st.session_state["last_bounds"] = None

# --- Layout ---
left_sidebar, main_col, right_sidebar = st.columns([2, 7, 3], gap="medium")

# --- Right Sidebar: Query and Metadata ---
with right_sidebar:
    st.header("Query")
    query = st.text_area(
        "Enter your query",
        value="Find eocis imagery for Berlin from October 2024",
        height=80,
        key="query_input"
    )
    search_btn = st.button("Search", key="search_btn", use_container_width=True)
    if search_btn:
        st.session_state["selected_id"] = None
        st.session_state["features"] = []
        st.session_state["result_ids"] = []
        st.session_state["metadata"] = None
        with st.spinner("Querying API (can take up to 30 seconds)..."):
            try:
                resp = requests.post(
                    "https://gwm6c6ucq5.execute-api.eu-west-1.amazonaws.com/prod/query",
                    json={"query": query},
                    timeout=35
                )
                resp.raise_for_status()
                data = resp.json()
                st.session_state["metadata"] = data.get("metadata", {})
                features = data.get("results", {}).get("features", [])
                st.session_state["features"] = features
                st.session_state["result_ids"] = [f.get("id") for f in features]
            except Exception as e:
                st.error(f"API request failed: {e}")

    if st.session_state["metadata"]:
        st.subheader("Metadata")
        st.json(st.session_state["metadata"])

# --- Left Sidebar: Result IDs ---
with left_sidebar:
    st.header("Results")
    if st.session_state["result_ids"]:
        for rid in st.session_state["result_ids"]:
            if st.button(rid, key=f"result_{rid}"):
                st.session_state["selected_id"] = rid
    else:
        st.info("No results yet. Submit a query.")

# --- Main Column: Map Display ---
with main_col:
    st.header("Map Display")
    # Default map center (Berlin)
    map_center = [52.5, 13.4]
    zoom = 8

    m = folium.Map(location=map_center, zoom_start=zoom, control_scale=True)

    selected_feature = None
    if st.session_state["selected_id"]:
        # Find the selected feature
        for f in st.session_state["features"]:
            if f.get("id") == st.session_state["selected_id"]:
                selected_feature = f
                break

    if selected_feature:
        geom = selected_feature.get("geometry")
        if geom:
            gj = folium.GeoJson(geom, name="Selected Feature", style_function=lambda x: {
                "color": "#FF5733", "weight": 3, "fillOpacity": 0.1
            })
            gj.add_to(m)
            # Compute bounds for zoom
            try:
                bounds = folium.GeoJson(geom).get_bounds()
                m.fit_bounds(bounds)
                st.session_state["last_bounds"] = bounds
            except Exception:
                pass

        # Display thumbnail if available
        assets = selected_feature.get("assets", {})
        thumbnail_url = None
        # Try common thumbnail asset keys
        for key in ["thumbnail", "visual", "overview"]:
            if key in assets and "href" in assets[key]:
                thumbnail_url = assets[key]["href"]
                break
        if thumbnail_url and geom:
            try:
                bounds = folium.GeoJson(geom).get_bounds()
                folium.raster_layers.ImageOverlay(
                    image=thumbnail_url,
                    bounds=bounds,
                    opacity=0.7,
                    interactive=True,
                    cross_origin=False
                ).add_to(m)
            except Exception:
                st.warning("Could not display thumbnail overlay.")

        st.success(f"Selected result: {selected_feature.get('id')}")
        st.write("Collection:", selected_feature.get("collection", ""))
        st.write("STAC Version:", selected_feature.get("stac_version", ""))
        st.write("Extensions:", selected_feature.get("stac_extensions", []))
    else:
        st.info("Select a result to display its geometry and thumbnail.")

    st_folium(m, width=900, height=600)
