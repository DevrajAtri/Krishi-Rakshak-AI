import os
import base64
from typing import Dict, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field


class PestCandidate(BaseModel):
    name: str = Field(description="The name of the potential pest identified in the image.")
    reasoning: str = Field(description="Visual evidence from the image explaining why this pest is a candidate.")

class PestAnalysis(BaseModel):
    candidates: List[PestCandidate] = Field(description="A list of 2-3 potential pests identified.")

# 2. IMAGE HELPER FUNCTION
def encode_image(image_path):
    """Encodes a local image file to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# 3. THE NODE FUNCTION
def image_analyze_node(state: Dict) -> Dict:
    
    image_path = state.get("image_path")
    
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0
    )
    
    
    structured_llm = llm.with_structured_output(PestAnalysis)
    
    base64_image = encode_image(image_path)
    
    SYSTEM_PROMPT = """
<Role>
You are an expert Agronomist and Plant Pathologist specialized in visual diagnosis of crop pests and diseases. 
Your goal is to analyze images of crops to identify potential pest infestations based strictly on visual symptoms.
</Role>

<Visual_Analysis_Guidelines>
When analyzing the image, follow this internal reasoning process:
1.  **Scan for Anomalies:** Look for discoloration (yellowing, browning), physical damage (holes, bites, chewing), or foreign objects (spots, webs, bugs).
2.  **Analyze Patterns:** Is the damage erratic (chewing) or systemic (yellowing veins)? Are there specific shapes (shot holes, serpentine mines)?
3.  **Hypothesize:** Based *only* on these visual cues, what are the top 3 most likely biological causes (pests)?
</Visual_Analysis_Guidelines>

<Examples>
Here is how you should formulate your reasoning.

[BAD Analysis]
Name: Aphids
Reasoning: Aphids are common in India and eat plants.

[GOOD Analysis]
Name: Aphids
Reasoning: I observe clusters of small, pear-shaped soft-bodied insects on the underside of the leaves. There is also visible "honeydew" residue and associated black sooty mold on the lower leaves, which is characteristic of sap-sucking aphid infestation.
</Examples>

<Task>
Analyze the provided image and identify 2 to 3 potential pest candidates.
For each candidate, provide the "Name" and the "Reasoning".
</Task>

<Constraints>
1.  **Visual Evidence Only:** If you say a pest is present, you must cite a visual feature visible in the image (e.g., "curled leaves," "white spots"). Do not guess based on probabilities unrelated to the image.
2.  **Uncertainty:** If the image is blurry, of a non-plant, or shows a healthy plant, explicitly state that in the reasoning or identifying "None" / "Healthy Plant" as the candidate.
3.  **No Location Bias:** Do not assume the location or season yet. Rely only on what the image shows.
</Constraints>
"""
    
    message = HumanMessage(
        content=[
            {"type": "text", "text": SYSTEM_PROMPT},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
            },
        ]
    )
    
    try:
        response: PestAnalysis = structured_llm.invoke([message])
        
        candidate_dict = {pest.name: pest.reasoning for pest in response.candidates}
        
        return {"candidate_analysis": candidate_dict}
        
    except Exception as e:
        
        print(f"Error in Image Analyzer: {e}")
        return {"candidate_analysis": {}, "error": str(e)}

