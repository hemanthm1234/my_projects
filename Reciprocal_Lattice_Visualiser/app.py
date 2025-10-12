import streamlit as st
import numpy as np
import plotly.graph_objects as go
from lattice_utils import generate_lattice, reciprocal_lattice
from scipy.spatial import Voronoi, ConvexHull

# -----------------------------------
# Streamlit Page Setup
# -----------------------------------
st.set_page_config(
    page_title="Reciprocal Lattice Visualizer",
    layout="wide",
    initial_sidebar_state="expanded"
)

import streamlit as st

# Using markdown for a more compact title with less vertical padding
st.sidebar.markdown("# ⚙️ Controls")

# --- Parameters Section ---
# Using bold markdown for a subheader that takes less space
st.sidebar.markdown("## **📐 Lattice Parameters**")
lattice_type = st.sidebar.selectbox(
    "Lattice Type", 
    ["Simple Cubic", "BCC", "FCC"],
    help="Select the crystal lattice structure."
)
a = st.sidebar.slider(
    "Lattice Constant (a)", 0.5, 5.0, 1.0, 0.01,
    help="The physical size of the unit cell."
)
N = st.sidebar.slider(
    "Number of Unit Cells", 1, 6, 3,
    help="Number of unit cells to render along each axis."
)
point_size = st.sidebar.slider(
    "Point Size", 2, 10, 3,
    help="The visual size of the lattice points."
)

st.sidebar.divider()

# --- Visibility Section ---
st.sidebar.markdown("## **👀 Visibility**")
show_real = st.sidebar.checkbox("Show Real Lattice", value=True)
show_recip = st.sidebar.checkbox("Show Reciprocal Lattice", value=True)
show_ws = st.sidebar.checkbox("Show Wigner–Seitz Cell", value=True)
show_bz = st.sidebar.checkbox("Show Brillouin Zone", value=True)

st.sidebar.divider()

# --- Legend Box with reduced vertical padding and margins ---
st.sidebar.markdown("""
<div style="
    background-color:#FFFFFF;
    border-radius:10px;
    padding: 10px 15px; /* Reduced vertical padding */
    border: 1px solid #e6e6e6;
">
    <h3 style="
        text-align:center;
        font-weight:bold;
        margin-top: 0;
        padding-bottom: 5px; /* Reduced space below title text */
        margin-bottom: 8px; /* Reduced space after title */
        border-bottom: 1px solid #ddd;
        color:#1B1212;
    ">
    Legend
    </h3>
    <div style="margin-bottom:3px;">🔵 <b style="color:#1f77b4;">Real Lattice</b></div>
    <div style="margin-bottom:3px;">🔴 <b style="color:#d62728;">Reciprocal Lattice</b></div>
    <div style="margin-bottom:3px;">🟦 <b style="color:#1f77b4;">Wigner–Seitz Cell</b></div>
    <div>🟥 <b style="color:#d62728;">Brillouin Zone</b></div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------
# Title
# -----------------------------------
st.markdown(
    "<h1 style='text-align:center;'>3️⃣D Reciprocal Lattice 🌐 Visualizer</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center;'>Interactively explore real-space and reciprocal-space lattices with their Wigner–Seitz and Brillouin zones.</p>",
    unsafe_allow_html=True,
)

# -----------------------------------
# Generate Lattices
# -----------------------------------
R, a_vecs = generate_lattice(lattice_type, a, N)
G = reciprocal_lattice(a_vecs, N)

# -----------------------------------
# Camera Persistence Setup
# -----------------------------------
if "camera" not in st.session_state:
    st.session_state.camera = None

def store_camera(view_data):
    if view_data and "scene.camera" in view_data:
        st.session_state.camera = view_data["scene.camera"]

# -----------------------------------
# Helper: Build Voronoi Cell (Wigner-Seitz or BZ)
# -----------------------------------
def voronoi_cell(points):
    """Compute the Voronoi region (convex hull) surrounding the origin."""
    vor = Voronoi(points)
    origin_idx = np.argmin(np.linalg.norm(vor.points, axis=1))
    region_index = vor.point_region[origin_idx]
    region = vor.regions[region_index]
    if -1 in region or len(region) == 0:
        return None, None
    verts = vor.vertices[region]
    hull = ConvexHull(verts)
    return verts, hull.simplices

# -----------------------------------
# Plot Setup
# -----------------------------------
fig = go.Figure()

# --- Real Lattice ---
if show_real:
    fig.add_trace(go.Scatter3d(
        x=R[:, 0], y=R[:, 1], z=R[:, 2],
        mode="markers",
        marker=dict(size=point_size, color="blue", opacity=0.8),
        name="Real Lattice"
    ))

# --- Reciprocal Lattice ---
if show_recip:
    fig.add_trace(go.Scatter3d(
        x=G[:, 0], y=G[:, 1], z=G[:, 2],
        mode="markers",
        marker=dict(size=point_size, color="red", opacity=0.8),
        name="Reciprocal Lattice"
    ))

# --- Wigner–Seitz Cell ---
if show_ws:
    ws_points = R[np.linalg.norm(R, axis=1) < a * 2.5]
    ws_vertices, ws_faces = voronoi_cell(ws_points)
    if ws_vertices is not None:
        fig.add_trace(go.Mesh3d(
            x=ws_vertices[:, 0], y=ws_vertices[:, 1], z=ws_vertices[:, 2],
            i=ws_faces[:, 0], j=ws_faces[:, 1], k=ws_faces[:, 2],
            opacity=0.25, color="#61F2F2", name="Wigner–Seitz Cell"
        ))

# --- Brillouin Zone ---
if show_bz:
    bz_points = G[np.linalg.norm(G, axis=1) < np.linalg.norm(G[1]) * 3]
    bz_vertices, bz_faces = voronoi_cell(bz_points)
    if bz_vertices is not None:
        fig.add_trace(go.Mesh3d(
            x=bz_vertices[:, 0], y=bz_vertices[:, 1], z=bz_vertices[:, 2],
            i=bz_faces[:, 0], j=bz_faces[:, 1], k=bz_faces[:, 2],
            opacity=0.3, color="#E37E5A", name="Brillouin Zone"
        ))

# -----------------------------------
# Layout / Camera
# -----------------------------------
layout_args = dict(
    scene=dict(
        xaxis_title="X",
        yaxis_title="Y",
        zaxis_title="Z",
        aspectmode="cube",
        bgcolor="rgba(0,0,0,0)"
    ),
    legend=dict(x=0, y=1),
    margin=dict(l=0, r=0, t=20, b=20),
    paper_bgcolor="rgba(0,0,0,0)"
)

if st.session_state.camera:
    layout_args["scene_camera"] = st.session_state.camera

fig.update_layout(**layout_args)

# -----------------------------------
# Display Chart and Capture Camera State
# -----------------------------------
st.plotly_chart(fig, use_container_width=True, key="plot")

# Optional: capture camera events if package available
try:
    from streamlit_plotly_events import plotly_events
    view_data = plotly_events(fig, override_height=700, click_event=False, hover_event=False, relayout_event=True)
    store_camera(view_data)
except Exception:
    pass

# -----------------------------------
# Instructions Section
# -----------------------------------
st.markdown("---") # Adds a horizontal line for visual separation
st.subheader("How to Use This Visualizer")
st.markdown("""
- **⚙️ Adjust Controls:** Use the sidebar on the left to select the lattice type (e.g., Simple Cubic, BCC), adjust the lattice constant ($a$), and set the number of unit cells to display.
- **👀 Toggle Visibility:** Use the checkboxes in the sidebar to show or hide different components:
    - **🔵 Real Lattice:** The crystal lattice in real physical space.
    - **🔴 Reciprocal Lattice:** The corresponding lattice in k-space (Fourier space).
    - **🟦 Wigner–Seitz Cell:** The primitive cell of the real lattice.
    - **🟥 Brillouin Zone:** The Wigner-Seitz cell of the reciprocal lattice.
- **🧭 Interact with the Plot:** Click and drag the plot to rotate the 3D view. Use your mouse scroll wheel to zoom in and out. The camera position is preserved as you change the settings.
""")

st.caption("<center>Made by Hemanth M</center>", unsafe_allow_html=True)