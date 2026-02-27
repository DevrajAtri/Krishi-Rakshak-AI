from typing import Dict, List, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

# --- PYDANTIC MODELS FOR STRUCTURED OUTPUT ---
class TreatmentImpact(BaseModel):
    chemical_name: str = Field(description="Name of the pesticide/chemical.")
    cost_estimate: str = Field(description="The estimated cost of the treatment.")
    toxicity_grade: str = Field(description="Grade from A (Bio-safe/Organic) to F (Highly Toxic/Synthetic).")
    water_risk: str = Field(description="Risk level for groundwater contamination (Low, Medium, High).")
    carbon_impact: str = Field(description="Estimated environmental/carbon footprint.")
    # --- NEW: The Analytical Engine ---
    calculation_and_logic: str = Field(description="Short, clear explanation of WHY these grades were given. Compare trade-offs (e.g., fast action vs. soil persistence) and justify risks based on chemical class, dosage, and location.")

class SustainabilityReport(BaseModel):
    treatments_analysis: List[TreatmentImpact] = Field(description="Analysis of each recommended treatment.")
    overall_eco_score: int = Field(description="An overall sustainability score from 1 to 100.")
    optimization_tip: str = Field(description="One clear, actionable tip. If only chemicals are found, provide a damage control protocol (e.g., buffer zones).")

def sustainability_analyzer_node(state: Dict) -> Dict:
    print("\n--- [Node E] Sustainability Analyzer: Evaluating Environmental Impact ---")
    
    pesticides_data = state.get("recommended_pesticides", [])
    crop = state.get("crop", "Unknown Crop")
    location = state.get("location", "Unknown Location")
    
    # If no pesticides were found, we skip the deep analysis
    if not pesticides_data:
        print("   ⚠️ No pesticides provided to analyze. Returning empty report.")
        return {"environmental_impact_report": None, "error": None}

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    structured_llm = llm.with_structured_output(SustainabilityReport)
    
    # --- UPDATED SYSTEM PROMPT ---
    SYSTEM_PROMPT = """
    <Role>
    You are an expert Environmental Agronomist and Sustainability Analyst.
    </Role>
    <Task>
    You will receive a list of proposed pesticide treatments (Biological and Synthetic) and their associated data.
    Analyze each treatment as a Transparent Decision Engine. 
    
    Crucial Instructions:
    1. For EACH treatment, provide a 'calculation_and_logic' paragraph. Explain the trade-offs (e.g., "Fast action but high persistence in soil (120+ days)" vs "Zero residue but requires 3x more frequent application").
    2. Justify risks based on the chemical class, dosage provided, and the specific Location's typical climate.
    3. Assign grades and provide an overall sustainability score (Heavily penalize toxic synthetics if bio-alternatives are available).
    4. Provide an 'optimization_tip'. If ONLY synthetic options exist, this tip MUST be a strict "Damage Control Protocol" (e.g., Nozzle types, 10-meter water buffer zones).
    </Task>
    """
    
    user_message = f"""
    Crop: {crop}
    Location: {location}
    Proposed Treatments data: {pesticides_data}
    
    Generate a full analytical sustainability and cost impact report.
    """

    try:
        response: SustainabilityReport = structured_llm.invoke([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ])
        
        report_dict = response.dict()
        print(f"   ✅ Eco-Score Calculated: {report_dict['overall_eco_score']}/100")
        
        return {
            "environmental_impact_report": report_dict,
            "error": None
        }

    except Exception as e:
        error_msg = f"Error in Sustainability Analyzer LLM call: {e}"
        print(f"   ❌ {error_msg}")
        
        # --- HACKATHON SAFETY NET ---
        print("   ⚠️ Crash detected. Injecting fallback sustainability report.")
        
        fallback_treatments = []
        for p in pesticides_data:
            # FIX: Updated keys to match Node C's Pydantic model
            name = p.get("chemical_name", "Unknown Chemical") if isinstance(p, dict) else str(p)
            cost = p.get("estimated_cost", "Data unavailable") if isinstance(p, dict) else "Data unavailable"
            is_synthetic = "synthetic" in str(p).lower()
            
            fallback_treatments.append({
                "chemical_name": name,
                "cost_estimate": str(cost),
                "toxicity_grade": "C (Moderate)" if is_synthetic else "A (Bio-safe)",
                "water_risk": "High" if is_synthetic else "Low",
                "carbon_impact": "High footprint" if is_synthetic else "Minimal footprint",
                "calculation_and_logic": f"Fallback Analysis: Based on standard profiles, this {'synthetic chemical' if is_synthetic else 'biological agent'} poses {'moderate ecological risks regarding soil persistence and runoff' if is_synthetic else 'minimal risks to local biodiversity'}."
            })

        fallback_report = {
            "treatments_analysis": fallback_treatments,
            "overall_eco_score": 50,
            "optimization_tip": "Maintain a 10-meter 'No-Spray Buffer' from water bodies and apply only during low-wind conditions to prevent ecological drift."
        }
        
        return {
            "environmental_impact_report": fallback_report,
            "error": str(e)
        }