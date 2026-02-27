from typing import Dict, List, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from search import search_web, format_search_results
from constants import PESTICIDE_DOMAINS

class PesticideInfo(BaseModel):
    chemical_name: str = Field(description="Active ingredient and formulation (e.g., 'Neem Oil 10000 ppm' or 'Chlorantraniliprole 18.5% SC').")
    category: str = Field(description="Must be strictly categorized as 'Biological/Natural' or 'Synthetic'.")
    brand_name: str = Field(description="Common trade name if mentioned (e.g., 'Coragen'), else 'Generic'.")
    dosage: str = Field(description="Exact precision application rate (e.g., '2ml/Litre'). If not explicitly found, output 'Standard baseline: Consult local dealer'.")
    safety_period: str = Field(description="Waiting period (PHI) in days if available, else 'Follow label'.")
    estimated_cost: str = Field(description="Estimated market cost per acre/litre in INR based on typical Indian context, or 'Data Unavailable'.")

class PesticideResponse(BaseModel):
    recommendations: List[PesticideInfo] = Field(description="List of up to 4 approved treatments, explicitly attempting to include BOTH Biological and Synthetic options for comparison.")
    natural_options_status: str = Field(description="Status message: e.g., 'Both Biological and Synthetic options found', or 'Only Synthetic options available for this pest.'")
    disclaimer: str = Field(description="Safety disclaimer (e.g., 'Wear protective gear').")

def pesticide_finder_node(state: Dict) -> Dict:
    print("\n--- [Node C] Pesticide Finder: Searching IPM & Approved Chemicals ---")
    
    confirmed_pest = state.get("confirmed_pest")
    crop = state.get("crop")
    
    if not confirmed_pest:
        print("   -> No pest confirmed. Skipping pesticide search.")
        return {
            "recommended_pesticides": [],
            "error": "No pest identified to treat."
        }

    # Broad query to catch sustainable and chemical options simultaneously
    query = f"Integrated Pest Management and chemical control for {confirmed_pest} in {crop} India"
    
    results = search_web(query, domains=PESTICIDE_DOMAINS, max_results=6)
    evidence = format_search_results(results)

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
    structured_llm = llm.with_structured_output(PesticideResponse)
    
    SYSTEM_PROMPT = """
<Role>
You are an expert Agricultural Sustainability Officer and Compliance Expert in India. 
Your mandate is to extract a comprehensive set of crop treatments—capturing BOTH organic/biological methods and synthetic chemical methods—to allow for environmental impact comparisons.
</Role>

<Input_Context>
You will receive "Search Evidence" containing text from Indian government agricultural portals (.gov.in) and research universities (.ac.in).
You must treat this evidence as the **Sole Source of Truth**. 
</Input_Context>

<Extraction_Guidelines>
Scan the Search Evidence for the following specific details:
1.  **Chemical/Biological Name:** Identify the active ingredient (e.g., "Neem Extract", "Beauveria bassiana", or "Imidacloprid").
2.  **Category:** Classify it accurately as 'Biological/Natural' or 'Synthetic'.
3.  **Formulation:** Look for the specific concentration (e.g., "18.5% SC", "1500 ppm").
4.  **Dosage:** Extract the exact precision application rate to prevent over-spraying.
5.  **Cost:** Estimate a standard Indian market cost if possible, otherwise note it as unavailable.
</Extraction_Guidelines>

<Thinking_Process>
1.  **Dual-Extraction:** Actively search for and list Bio-pesticides (IPM, botanical extracts) AND Synthetic chemicals. You must try to provide at least one of each if the evidence supports it.
2.  **Verify Status:** Update the `natural_options_status` to reflect what was found (e.g., "Both found", "Only synthetic found").
3.  **Refine Dosage:** Ensure the dosage is specific enough to prevent ecological runoff (e.g., precise ml/Litre).
</Thinking_Process>

<Output_Constraint_Checklist>
[ ] Did I attempt to extract both Biological AND Synthetic options for a comparative analysis? (Required)
[ ] Is the Category strictly 'Biological/Natural' or 'Synthetic'? (Required)
[ ] Is the dosage highly specific or safely defaulted? (Required to prevent resource waste)
</Output_Constraint_Checklist>

<Task>
Based *strictly* on the provided Search Evidence, generate a structured list of treatments.
</Task>
"""
    
    user_message = f"""
    Context:
    Pest: {confirmed_pest}
    Crop: {crop}
    
    Search Evidence (Official Sources):
    {evidence}
    
    Task: Extract a mix of biological and synthetic treatments.
    """

    try:
        response: PesticideResponse = structured_llm.invoke([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ])
        
        detailed_info = [item.dict() for item in response.recommendations]
        
        print(f"   ✅ Found {len(detailed_info)} options.")
        print(f"   🌱 Status: {response.natural_options_status}")

        return {
            "recommended_pesticides": detailed_info, 
            "error": None
        }

    except Exception as e:
        print(f"   ❌ Error in Pesticide Finder: {e}")
        return {
            "recommended_pesticides": [], 
            "error": str(e)
        }

if __name__ == "__main__":
    test_state = {
        "confirmed_pest": "Yellow Stem Borer",
        "crop": "Rice"
    }
    
    result = pesticide_finder_node(test_state)
    import json
    print(json.dumps(result, indent=2))