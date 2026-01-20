from typing import Dict, List, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from search import search_web, format_search_results
from constants import PESTICIDE_DOMAINS

class PesticideInfo(BaseModel):
    chemical_name: str = Field(description="Active ingredient and formulation (e.g., 'Chlorantraniliprole 18.5% SC').")
    brand_name: str = Field(description="Common trade name if mentioned (e.g., 'Coragen'), else 'Generic'.")
    dosage: str = Field(description="Application rate per acre or hectare.")
    safety_period: str = Field(description="Waiting period (PHI) in days if available, else 'Follow label'.")

class PesticideResponse(BaseModel):
    recommendations: List[PesticideInfo] = Field(description="List of 2-3 government-approved pesticides found in the search results.")
    disclaimer: str = Field(description="Safety disclaimer (e.g., 'Wear protective gear').")

def pesticide_finder_node(state: Dict) -> Dict:
    print("\n--- [Node C] Pesticide Finder: Searching Approved Chemicals ---")
    
    confirmed_pest = state.get("confirmed_pest")
    crop = state.get("crop")
    
    if not confirmed_pest:
        print("   -> No pest confirmed. Skipping pesticide search.")
        return {
            "recommended_pesticides": [],
            "detailed_pesticide_info": [],
            "error": "No pest identified to treat."
        }

    query = f"recommended insecticides for {confirmed_pest} in {crop} India"
    
    results = search_web(query, domains=PESTICIDE_DOMAINS, max_results=6)
    evidence = format_search_results(results)

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
    structured_llm = llm.with_structured_output(PesticideResponse)
    
    SYSTEM_PROMPT = """
<Role>
You are a government-authorized Agricultural Compliance Officer in India. 
Your mandate is to extract and recommend *only* CIBRC (Central Insecticides Board & Registration Committee) approved chemical interventions from the provided official reports.
</Role>

<Input_Context>
You will receive "Search Evidence" containing text from Indian government agricultural portals (.gov.in) and research universities (.ac.in).
You must treat this evidence as the **Sole Source of Truth**. 
</Input_Context>

<Extraction_Guidelines>
Scan the Search Evidence for the following specific details:
1.  **Chemical Name:** Identify the active ingredient (e.g., "Chlorantraniliprole", "Imidacloprid").
2.  **Formulation:** Look for the specific concentration (e.g., "18.5% SC", "17.8% SL"). This is critical for dosage accuracy.
3.  **Dosage:** Extract the exact application rate mentioned (e.g., "60 ml per acre" or "0.5 ml per liter of water").
4.  **Safety:** Look for Pre-Harvest Intervals (PHI) or specific warnings (e.g., "Do not use on fodder crops").
</Extraction_Guidelines>

<Thinking_Process>
1.  **Filter:** Ignore any "botanical" or "home-made" remedies (like Neem cake, ash, cow urine) unless the user explicitly requested organic options. Focus on synthetic chemicals for immediate control unless none are found.
2.  **Verify:** Does the text explicitly link this chemical to the specific *Pest* and *Crop* provided in the context?
    * *If yes:* Add to recommendations.
    * *If no (e.g., it lists it for a different crop):* Discard it.
3.  **Refine:** Normalize the dosage instructions to be farmer-friendly.
</Thinking_Process>

<Output_Constraint_Checklist>
[ ] Did I include the Formulation (SC/EC/WG)? (Required)
[ ] Is this chemical mentioned in the provided text? (Required - No Hallucinations)
[ ] Is the dosage specific? (Reject vague advice like "apply pesticide")
</Output_Constraint_Checklist>

<Task>
Based *strictly* on the provided Search Evidence, generate a structured list of approved pesticides.
If the evidence mentions no specific chemicals, return an empty list with a disclaimer.
</Task>
"""
    
    user_message = f"""
    Context:
    Pest: {confirmed_pest}
    Crop: {crop}
    
    Search Evidence (Official Sources):
    {evidence}
    
    Task: Extract approved pesticides.
    """

    try:
        response: PesticideResponse = structured_llm.invoke([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ])
        
        simple_names = [item.chemical_name for item in response.recommendations]
        detailed_info = [item.dict() for item in response.recommendations]
        
        print(f"   ✅ Found {len(simple_names)} options: {simple_names}")

        return {
            "recommended_pesticides": simple_names, 
            "detailed_pesticide_info": detailed_info,
            "error": None
        }

    except Exception as e:
        print(f"   ❌ Error in Pesticide Finder: {e}")
        return {
            "recommended_pesticides": [], 
            "detailed_pesticide_info": [],
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