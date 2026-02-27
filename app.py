import streamlit as st
import tempfile
import os
from typing import Dict, List, Any
from dotenv import load_dotenv
load_dotenv()

from graph import app  
from constants import STATE_SUBSIDY_DOMAINS

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Agri-Agent | Sustainability Command Center",
    page_icon="🌿",
    layout="wide"
)

# --- CUSTOM CSS STYLING (The Professional "Green UI" Look) ---
# Replace your current st.markdown("""<style>...""") with this:

st.markdown("""
<style>
    /* Force Light Theme Text Colors globally */
    .stApp {
        background-color: #F9F5F2; /* Light Sandstone Background */
        font-family: 'Inter', sans-serif;
    }
    
    /* Force standard markdown text to be dark */
    div[data-testid="stMarkdownContainer"] p, 
    div[data-testid="stMarkdownContainer"] h1, 
    div[data-testid="stMarkdownContainer"] h2, 
    div[data-testid="stMarkdownContainer"] h3, 
    div[data-testid="stMarkdownContainer"] li {
        color: #2E2E2E !important;
    }

    /* Modern Dashboard Headers */
    .main-header {
        font-size: 2.5rem;
        color: #1B5E20 !important; 
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 0rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555555 !important;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #1B5E20 !important;
        font-weight: 700;
        margin-top: 1rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #8A9668; 
        padding-bottom: 0.5rem;
    }
    
    /* KPI Status Bar */
    .kpi-container {
        display: flex;
        justify-content: space-around;
        background: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
        border-top: 4px solid #F4C93B; 
    }
    .kpi-metric { text-align: center; }
    .kpi-value { font-size: 1.4rem; font-weight: 700; color: #1B5E20 !important; }
    .kpi-label { font-size: 0.9rem; color: #666666 !important; }

    /* Diagnosis Card (Left Column) */
    .diagnosis-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.03);
        height: 100%;
        color: #2E2E2E;
    }

    /* Main Decision Matrix Card (Centerpiece) */
    .decision-matrix-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.05);
        border: 1px solid #E0DED0;
        color: #2E2E2E;
    }
    
    /* Individual Treatment Comparison Cards */
    .bio-card {
        border-left: 5px solid #8A9668; 
        background: #F4F6F0;
        padding: 1.2rem;
        margin-bottom: 1rem;
        border-radius: 8px;
        color: #2E2E2E !important;
    }
    .synth-card {
        border-left: 5px solid #D32F2F; 
        background: #FFF0F0;
        padding: 1.2rem;
        margin-bottom: 1rem;
        border-radius: 8px;
        color: #2E2E2E !important;
    }
    .card-title {
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        color: #1B5E20 !important;
    }
    .metric-row {
        display: flex;
        justify-content: space-between;
        font-size: 0.9rem;
        color: #333333 !important;
        margin-bottom: 0.3rem;
    }

    /* Logic & Reasoning Box */
    .logic-box {
        background-color: #E8F5E9;
        border: 1px solid #C8E6C9;
        padding: 1.5rem;
        border-radius: 10px;
        margin-top: 1.5rem;
        color: #2E2E2E !important;
    }
    .logic-header {
        font-weight: 700;
        color: #1B5E20 !important;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
    }

    /* Subsidy Card */
    .subsidy-card {
        background: white;
        border-left: 5px solid #F4C93B;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        color: #2E2E2E !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR INPUTS ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=70) # Updated icon
    st.markdown("### Field Data Input")

    with st.form("analysis_form"):
        uploaded_file = st.file_uploader(
            "Upload Crop Image", 
            type=["jpg", "jpeg", "png"]
        )

        state_list = sorted(list(STATE_SUBSIDY_DOMAINS.keys()))
        default_index = state_list.index("Punjab") if "Punjab" in state_list else 0
        location = st.selectbox("State / Region", state_list, index=default_index)

        col1, col2 = st.columns(2)
        with col1:
            month = st.selectbox(
                "Current Month",
                ["January", "February", "March", "April", "May", "June",
                 "July", "August", "September", "October", "November", "December"],
                index=0
            )
        with col2:
            crop = st.text_input("Crop Name", value="Wheat")

        run_btn = st.form_submit_button(
            "🚀 Initialize Analysis", 
            use_container_width=True
        )

    if st.button("🔄 New Session"):
        st.session_state.clear()
        st.rerun()

# --- MAIN DASHBOARD HEADER ---
st.markdown('<div class="main-header">🌿 Agri-Agent Command Center</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Driven Pest Diagnostics & Resource Optimization Engine</div>', unsafe_allow_html=True)


# --- MAIN APP LOGIC ---
if run_btn and uploaded_file:
    
    # 1. SAVE IMAGE
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        temp_image_path = tmp_file.name

    # 2. RUN THE AI PIPELINE (with status spinner)
    with st.spinner("Processing Field Data... Organizing Sustainability Protocols..."):
        initial_state = {
            "image_path": temp_image_path,
            "location": location,
            "month": month,
            "crop": crop,
            "recommended_pesticides": [],
            "environmental_impact_report": None,
            "subsidy_info": []
        }
        final_state = app.invoke(initial_state)

    # 3. EXTRACT DATA FOR DASHBOARD
    pest_name = final_state.get("confirmed_pest", "Unknown")
    confidence = final_state.get("confidence_score", 0.0)
    reasoning = final_state.get("decision_reasoning", "")
    treatments = final_state.get("recommended_pesticides", [])
    eco_report = final_state.get("environmental_impact_report")
    subsidies = final_state.get("subsidy_info", [])

    # 4. TOP KPI STATUS BAR
    st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-metric">
                <div class="kpi-value">{pest_name}</div>
                <div class="kpi-label">Target Pest Detected</div>
            </div>
            <div class="kpi-metric">
                <div class="kpi-value">{confidence * 100:.1f}%</div>
                <div class="kpi-label">Diagnostic Confidence</div>
            </div>
            <div class="kpi-metric">
                <div class="kpi-value">{location}, {month}</div>
                <div class="kpi-label">Environmental Context</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 5. MAIN ASYMMETRICAL LAYOUT (1/4 Left, 3/4 Right)
    col_diag, col_decision = st.columns([1, 3], gap="medium")

    # --- LEFT COLUMN: DIAGNOSIS CASE FILE ---
    with col_diag:
        st.markdown('<div class="section-header">📋 Case File</div>', unsafe_allow_html=True)
        with st.container(border=False):
            st.markdown('<div class="diagnosis-card">', unsafe_allow_html=True)
            st.image(uploaded_file, caption="Visual Evidence", use_container_width=True)
            
            st.markdown("#### 🕵️ Verification Summary")
            st.info(reasoning.split('.')[0] + ".") # Show just the first sentence for crispness
            with st.expander("View Full Cross-Reference Data"):
                 st.write(reasoning)
            st.markdown('</div>', unsafe_allow_html=True)

    # --- RIGHT COLUMN: THE SUSTAINABILITY DECISION ENGINE ---
    with col_decision:
        st.markdown('<div class="section-header">🧠 Treatment Decision Engine & Sustainability Matrix</div>', unsafe_allow_html=True)
        
        with st.container(border=False):
             st.markdown('<div class="decision-matrix-card">', unsafe_allow_html=True)

             # A. Separate Biological vs Synthetic Options
             bio_opts = [t for t in treatments if "biological" in str(t.get('category','')).lower() or "natural" in str(t.get('category','')).lower()]
             synth_opts = [t for t in treatments if "synthetic" in str(t.get('category','')).lower()]
             
             # B. Side-by-Side Comparison Columns
             col_bio, col_synth = st.columns(2, gap="large")

             with col_bio:
                 st.markdown("### 🌿 Biological / IPM Options (Preferred)")
                 if bio_opts:
                     for t in bio_opts:
                         st.markdown(f"""
                         <div class="bio-card">
                             <div class="card-title">{t.get('chemical_name')}</div>
                             <div class="metric-row"><span>📦 Dosage:</span> <strong>{t.get('dosage')}</strong></div>
                             <div class="metric-row"><span>💰 Est. Cost:</span> <span>₹{t.get('estimated_cost')}</span></div>
                         </div>
                         """, unsafe_allow_html=True)
                 else:
                     st.warning("No specific biological options found in current CIBRC database for this severity.")

             with col_synth:
                 st.markdown("### 🧪 Synthetic Options (Higher Impact)")
                 if synth_opts:
                     for t in synth_opts:
                         st.markdown(f"""
                         <div class="synth-card">
                             <div class="card-title">{t.get('chemical_name')}</div>
                             <div class="metric-row"><span>📦 Dosage:</span> <strong>{t.get('dosage')}</strong></div>
                             <div class="metric-row"><span>💰 Est. Cost:</span> <span>₹{t.get('estimated_cost')}</span></div>
                         </div>
                         """, unsafe_allow_html=True)
                 else:
                    st.info("No specific synthetic chemical recommendations necessary based on current data.")

             # C. The AI Logic Core (Node E Output)
             if eco_report:
                score = eco_report.get("overall_eco_score", 0)
                
                st.markdown("""<div class="logic-box">
                    <div class="logic-header">🤖 AI Sustainability Logic & Trade-off Analysis</div>
                    """, unsafe_allow_html=True)
                
                # 1. Overall Score Visualization
                col_gauge, col_text = st.columns([1, 3])
                with col_gauge:
                     st.metric("Protocol Eco-Score", f"{score}/100", delta="Sustainable" if score > 70 else "High Impact", delta_color="normal" if score > 70 else "inverse")
                with col_text:
                     # Display the Optimization Tip
                     st.markdown(f"**💡 Resource Optimization Strategy:** {eco_report.get('optimization_tip')}")

                st.markdown("---")
                # 2. Detailed Comparative Logic from Node E
                st.markdown("#### ⚖️ Comparative Risk Calculation:")
                treatment_analysis = eco_report.get("treatments_analysis", [])
                if treatment_analysis:
                    for analysis in treatment_analysis:
                        icon = "🌿" if "A" in analysis.get('toxicity_grade','') or "B" in analysis.get('toxicity_grade','') else "🧪"
                        st.markdown(f"""
                        **{icon} {analysis.get('chemical_name')}:** {analysis.get('calculation_and_logic')}
                        """)
                        # Small metric pills below the logic
                        st.caption(f"Toxicity: {analysis.get('toxicity_grade')} | Water Risk: {analysis.get('water_risk')} | Carbon: {analysis.get('carbon_impact')}")
                        st.markdown("<br>", unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True) # End logic-box

             st.markdown('</div>', unsafe_allow_html=True) # End decision-matrix-card

    # 6. BOTTOM SECTION: SUBSIDIES
    st.markdown('<div class="section-header">🏦 Available Financial Support & Schemes</div>', unsafe_allow_html=True)
    if subsidies:
        cols = st.columns(3) # Display in 3 columns for a cleaner look
        for i, s in enumerate(subsidies):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="subsidy-card">
                    <strong>{s.get('scheme_name')}</strong><br>
                    <span style="font-size:0.9rem">{s.get('benefit_details')}</span><br>
                    <em style="font-size:0.8rem; color:#666">Eligibility: {s.get('eligibility')}</em>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info(f"No specific online schemes registered for {crop} in {location} currently. Contact local Krishi Vigyan Kendra (KVK).")


    # Cleanup
    if 'temp_image_path' in locals():
        os.remove(temp_image_path)

elif run_btn and not uploaded_file:
    st.warning("⚠️ Please upload a field image to initiate analysis.")
else:
    st.info("👈 awaiting input parameters to initialize command center...")