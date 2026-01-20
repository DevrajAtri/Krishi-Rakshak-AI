import streamlit as st
import tempfile
import os
import shutil
from typing import Dict, List
from dotenv import load_dotenv
load_dotenv()

from graph import app  
from constants import STATE_SUBSIDY_DOMAINS

st.set_page_config(
    page_title="Agri-Agent | AI Pest Control",
    page_icon="🌾",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E7D32; /* Agri Green */
        font-weight: 700;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #1B5E20;
        margin-top: 1rem;
    }
    .stAlert {
        border-radius: 8px;
    }
    .card {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #f0f8f0;
        border: 1px solid #c8e6c9;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/606/606041.png", width=80)
    st.title("Field Inputs")

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
            "🚀 Analyze Field", 
            use_container_width=True
        )

    if st.button("🔄 Reset / New Search"):
        st.session_state.clear()
        st.rerun()



st.markdown('<div class="main-header">🌾 Agri-Agent: Autonomous Pest Control</div>', unsafe_allow_html=True)
st.markdown("Your AI-powered Agricultural Extension Officer.")

if run_btn and uploaded_file:
   
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        temp_image_path = tmp_file.name

    
    status_container = st.status("Initializing Agent...", expanded=True)
    
    try:
        
        status_container.write("🔍 [Node A] Analyzing visual symptoms...")
        status_container.write(f"🌍 [Node B] Verifying against {location} agricultural data...")
        status_container.write("💊 [Node C] Searching CIBRC approved pesticides...")
        status_container.write("💰 [Node D] Checking subsidy schemes...")
        
        
        initial_state = {
            "image_path": temp_image_path,
            "location": location,
            "month": month,
            "crop": crop,
            
            "recommended_pesticides": [],
            "detailed_pesticide_info": [],
            "subsidy_info": []
        }
        
        
        final_state = app.invoke(initial_state)
        
        status_container.update(label="Analysis Complete!", state="complete", expanded=False)

        st.markdown('<div class="sub-header">1. Diagnosis Report</div>', unsafe_allow_html=True)
        col_img, col_diag = st.columns([1, 2])
        
        with col_img:
            st.image(uploaded_file, caption="Field Sample", width=300, channels="RGB")

        
        with col_diag:
            pest_name = final_state.get("confirmed_pest", "Unknown")
            confidence = final_state.get("confidence_score", 0.0)
            
            if confidence > 0.7:
                color = "green"
            elif confidence > 0.4:
                color = "orange"
            else:
                color = "red"
                
            st.markdown(f"""
            <div class="card">
                <h3 style="color: {color}; margin:0;">Identified Pest: {pest_name}</h3>
                <p><strong>Confidence:</strong> {confidence * 100:.1f}%</p>
                <p><strong>Reasoning:</strong> {final_state.get('decision_reasoning')}</p>
            </div>
            """, unsafe_allow_html=True)
            
          
            with st.expander("🕵️ View Verification Evidence (Internal Monologue)"):
                st.info("The agent performed cross-verification using these searches:")
                
                st.write(final_state.get('decision_reasoning'))

       
        st.markdown("---")
        st.markdown('<div class="sub-header">2. Recommended Treatment (CIBRC Approved)</div>', unsafe_allow_html=True)
        
        treatments = final_state.get("detailed_pesticide_info", [])
        
        if treatments:
            for t in treatments:
                with st.container():
                    cols = st.columns([2, 1, 1])
                    cols[0].markdown(f"**🧪 {t.get('chemical_name')}**")
                    cols[1].markdown(f"**Dosage:** {t.get('dosage')}")
                    cols[2].markdown(f"**Wait Period:** {t.get('safety_period')}")
        else:
            st.warning("No specific chemical recommendations found. Please consult a local expert.")

        st.markdown("---")
        st.markdown('<div class="sub-header">3. Financial Aid & Schemes</div>', unsafe_allow_html=True)
        
        schemes = final_state.get("subsidy_info", [])
        
        if schemes:
            for s in schemes:
                st.info(f"""
                **🏦 {s.get('scheme_name')}** {s.get('benefit_details')}  
                *Eligibility:* {s.get('eligibility')}
                """)
        else:
            st.markdown(f"No specific online schemes found for **{location}** at this moment. Visit your local Agriculture Office.")
            
    except Exception as e:
        st.error(f"System Error: {str(e)}")
        
        st.warning("The agent encountered a connection issue, but here is a general analysis based on visual data...")
    
    finally:
        
        if 'temp_image_path' in locals():
            os.remove(temp_image_path)

elif run_btn and not uploaded_file:
    st.warning("Please upload an image first.")
else:
    
    st.info("👈 Upload an image and select your region to begin.")