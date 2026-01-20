from typing import Dict, Optional, List, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from search import search_web, format_search_results
from constants import VERIFICATION_DOMAINS

class PestConclusion(BaseModel):
    confirmed_pest: str = Field(
        description="The name of the single best-matching pest. Return 'None' if no candidate is supported by the evidence."
    )
    confidence_score: float = Field(
        description="A score between 0.0 (unsure) and 1.0 (certain).",
        ge=0.0,
        le=1.0
    )
    decision_reasoning: str = Field(
        description="A concise explanation of why this pest was chosen over others, referencing the search evidence."
    )

def pest_detector_node(state: Dict) -> Dict:
    print("\n--- [Node B] Pest Detector: Verifying Candidates ---")
    
    candidates = state.get("candidate_analysis", {})
    location = state.get("location")
    month = state.get("month")
    crop = state.get("crop")
    
    if not candidates:
        print("   -> No visual candidates provided. Exiting.")
        return {
            "confirmed_pest": None, 
            "confidence_score": 0.0,
            "decision_reasoning": "No pest candidates were identified from the image."
        }

    aggregated_evidence = ""
    print(f"   -> Investigating {len(candidates)} candidates for '{crop}' in '{location}' during '{month}'.")
    
    for pest_name, visual_reasoning in candidates.items():
        query = f"{pest_name} infestation on {crop} in {location} during {month}"
        
        results = search_web(query, domains=VERIFICATION_DOMAINS, max_results=2)
        formatted_results = format_search_results(results)
        
        aggregated_evidence += f"\n=== CANDIDATE: {pest_name} ===\n"
        aggregated_evidence += f"[Visual Evidence from Image]: {visual_reasoning}\n"
        aggregated_evidence += f"[Search Query Used]: {query}\n"
        aggregated_evidence += f"[Search Findings]:\n{formatted_results}\n"
        aggregated_evidence += "================================\n"

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    structured_llm = llm.with_structured_output(PestConclusion)
    
    SYSTEM_PROMPT = """
<Role>
You are an expert Agricultural Entomologist and Data Verification Specialist. 
Your specific task is to cross-reference visual pest identification candidates against environmental facts (Location, Season, Crop) and real-time search evidence.
</Role>

<Input_Structure>
You will receive:
1. **Context:** The user's specific Crop, Location, and Month.
2. **Visual Candidates:** A list of pests suspected by the vision system.
3. **Evidence Dossier:** Real-world search results confirming or denying the presence of these pests in the given context.
</Input_Structure>

<Thinking_Process>
Before answering, perform this internal "Verification Loop" for EACH candidate:

1.  **Context Check:** Does the Search Evidence explicitly mention that this pest attacks [Crop] in [Location] during or around [Month]?
    * *Strong Match:* Evidence says "Pest X outbreaks common in Punjab in October."
    * *Weak Match:* Evidence mentions the pest but in a different season or region.
    * *Rejection:* Evidence says "Pest X is dormant in Winter" or "Does not attack [Crop]."

2.  **Visual Confirmation:** Compare the "Visual Reasoning" provided against the description in the Search Evidence.
    * Do the search results describe the same symptoms (e.g., "shot holes," "white patches") as the vision node?

3.  **Conflict Resolution:**
    * IF Visuals = High Confidence BUT Search Evidence = "Impossible in this season" -> **REJECT** (Trust the season).
    * IF Visuals = Medium Confidence AND Search Evidence = "Highly active now" -> **CONFIRM** (Context validates the guess).
</Thinking_Process>

<Examples>
[Example 1: Strong Confirmation]
Candidate: "Stem Borer"
Context: Rice, Odisha, August
Evidence: "Yellow Stem Borer is a major pest in Odisha Kharif rice (July-Oct)."
Decision: Confirmed.

[Example 2: Contextual Rejection]
Candidate: "Aphids"
Context: Cotton, Rajasthan, June (45°C)
Evidence: "Aphids require cool, humid weather. Population collapses in high heat."
Decision: None (Reasoning: Environmental conditions do not support infestation).
</Examples>

<Task>
Identify the SINGLE most likely pest.
1.  If the evidence is strong, output the **Confirmed Pest Name**.
2.  If the evidence is contradictory or non-existent for all candidates, output **"None"**.
3.  Provide a **Confidence Score** (0.0 to 1.0) based on the strength of the overlap between Visuals and Evidence.
</Task>

<Constraints>
* **Needle in a Haystack:** Do not ignore the Search Evidence. If the evidence says a pest is NOT found in that state, you MUST reject it.
* **No Hallucination:** Do not invent a pest name that is not in the Candidates list.
* **Decision:** You must choose one of the provided candidates or "None".
</Constraints>
"""
    
    user_message = f"""
    <Context>
    Location: {location}
    Month: {month}
    Crop: {crop}
    </Context>

    <Evidence_Dossier>
    {aggregated_evidence}
    </Evidence_Dossier>

    Based on the context and evidence above, identify the confirmed pest.
    """

    try:
        print("   -> Asking AI to make the final decision...")
        response = structured_llm.invoke([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ])
        
        final_pest = response.confirmed_pest
        confidence = response.confidence_score
        reasoning = response.decision_reasoning

        if not final_pest or final_pest.lower() in ["none", "unknown"]:
            print("   ⚠️ LLM returned None. Forcing fallback to top visual candidate.")
           
            final_pest = list(candidates.keys())[0]
            confidence = 0.4 
            reasoning += f" (Note: Verification inconclusive. Defaulting to most likely visual diagnosis: {final_pest}.)"
            
        print(f"   ✅ Final Decision: {final_pest} (Confidence: {confidence:.2f})")

        return {
            "confirmed_pest": final_pest,
            "confidence_score": confidence,
            "decision_reasoning": reasoning,
            "error": None
        }

    except Exception as e:
        error_msg = f"Error in Pest Detector LLM call: {e}"
        print(f"   ❌ {error_msg}")
        
        print("   ⚠️ Crash detected. Forcing fallback to top visual candidate.")
        fallback_pest = list(candidates.keys())[0]
        
        return {
            "confirmed_pest": fallback_pest,
            "confidence_score": 0.1,
            "decision_reasoning": f"System error during verification ({str(e)}). Defaulting to visual diagnosis: {fallback_pest}.",
            "error": str(e)
        }