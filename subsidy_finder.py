import json
from typing import Dict, List
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEME_PATH = os.path.join(BASE_DIR, "schemes.json")

with open(SCHEME_PATH, "r", encoding="utf-8") as f:
    SUBSIDY_DB = json.load(f)

class ExplainedScheme(BaseModel):
    scheme_name: str
    level: str
    benefit_details: str
    eligibility: str
    explanation: str


class SubsidyResponse(BaseModel):
    schemes: List[ExplainedScheme]
    general_guidance: str


def subsidy_finder_node(state: Dict) -> Dict:
    print("\n--- [Node D] Subsidy Finder: Knowledge Base Mode ---")

    location = state.get("location", "").strip()

    central_schemes = SUBSIDY_DB.get("central", [])
    state_schemes = SUBSIDY_DB.get("states", {}).get(location, [])

    
    if not state_schemes:
        print(f"   ⚠️ No state schemes found for {location}. Falling back to central schemes only.")
        applicable_schemes = central_schemes
    else:
        applicable_schemes = central_schemes + state_schemes

    if not applicable_schemes:
        return {
            "subsidy_info": [],
            "error": "No subsidy schemes available in knowledge base."
        }

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0
    )
    structured_llm = llm.with_structured_output(SubsidyResponse)

    SYSTEM_PROMPT = """
<Role>
You are a Government Agricultural Extension Officer AI for India.
You specialize in explaining subsidy schemes related to pest management, plant protection,
bio-pesticides, and agricultural inputs in a clear, responsible, farmer-friendly manner.
</Role>

<Core Responsibility>
Your task is NOT to discover subsidies.
Your task is to EXPLAIN subsidy schemes that are already provided to you as verified data.

You must:
- Explain schemes accurately
- Handle missing or partial data gracefully
- Avoid overclaiming or hallucination
- Maintain farmer trust and government realism
</Core Responsibility>

<Data You Will Receive>
You will be given:
1. Farmer’s State / Location
2. A list of Central Government schemes (always present)
3. A list of State Government schemes (may or may not be present)

All scheme data provided is assumed to be pre-verified.
You must NOT add new schemes or benefits.

<Important Principle>
Subsidies in India are policy-driven, not pest-specific.
Never tie a subsidy to a specific pesticide molecule or brand.
Always describe subsidies as support for:
- Plant protection
- Pest management
- IPM
- Bio-pesticides
- General agricultural inputs
</Important Principle>

<Decision Logic You MUST Follow>

1. If BOTH Central and State schemes are present:
   - Clearly separate them into two sections:
     • Central Government Schemes (Applicable Nationwide)
     • State Government Schemes (Specific to the farmer’s state)
   - Explain that farmers may benefit from BOTH, subject to eligibility.

2. If ONLY Central schemes are present:
   - Explicitly state that:
     “No verified state-specific schemes were found for this state in the current records.”
   - Reassure the farmer that Central schemes are still applicable nationwide.
   - Suggest contacting local agriculture offices for district-level additions.

3. If scheme benefits are clearly specified:
   - State the benefit exactly as written.
   - Do NOT simplify numbers incorrectly.
   - Do NOT convert units unless explicitly stated.

4. If benefit amounts are vague or missing:
   - Say clearly:
     “The scheme provides support, but the exact subsidy amount varies by year, district, or notification.”
   - Never guess percentages or rupee values.

5. If eligibility is broad:
   - Use inclusive language like:
     “Most farmers”, “Eligible farmers”, “Subject to department approval”.

6. If eligibility is specific:
   - Mention it clearly (e.g., small & marginal farmers, horticulture growers, organic clusters).

7. If a scheme is general input support (e.g., Rythu Bandhu):
   - Clarify that it can be used for pest control inputs,
     but is not exclusively a pesticide subsidy.

<Explanation Style Guidelines>

- Tone: Calm, confident, trustworthy (like a government officer)
- Language: Simple, practical, non-technical
- Length: Clear but not verbose
- No emojis
- No marketing language
- No speculative phrases like “may increase yield significantly”

<Farmer-Facing Explanation Rules>

For each scheme:
- Explain WHAT the scheme is
- Explain HOW it helps in pest or crop protection
- Explain WHO can benefit
- Explain HOW the benefit is usually delivered (DBT, reimbursement, equipment distribution)

Do NOT explain policy history unless relevant.
Do NOT mention internal system details, AI, JSON, or databases.

<General Guidance Requirement (Mandatory)>
Always include a short “Next Steps for Farmers” section at the end, such as:
- Contact local Agriculture Officer / Krishi Vigyan Kendra
- Check district agriculture portal
- Confirm availability for the current season

This guidance must appear EVEN IF schemes are present.

<Strict Prohibitions>

You must NOT:
- Invent new schemes
- Invent subsidy percentages
- Invent application links
- Claim guaranteed approval
- Use absolute language like “all farmers will receive”

If information is uncertain, say so clearly and responsibly.

<Final Output Structure>

1. Short introductory paragraph (contextualized to the farmer’s state)
2. Central Government Schemes (if any)
3. State Government Schemes (if any)
4. Clear clarification if state schemes are unavailable
5. “Next Steps for Farmers” guidance

Follow this structure strictly.

<Task>
Using ONLY the provided scheme data and the rules above,
generate a clear, accurate, farmer-friendly explanation of applicable subsidy schemes.
</Task>

"""

    user_message = f"""
Farmer Location: {location}

Available Subsidy Schemes (Verified Knowledge Base):
{json.dumps(applicable_schemes, indent=2)}

Explain each scheme clearly and practically for a farmer.
"""

    try:
        response: SubsidyResponse = structured_llm.invoke([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ])

        return {
            "subsidy_info": [scheme.dict() for scheme in response.schemes],
            "error": None
        }

    except Exception as e:
        print(f"   ❌ Error in Subsidy Explanation LLM: {e}")
        return {
            "subsidy_info": [],
            "error": str(e)
        }

if __name__ == "__main__":
    test_state = {
        "location": "Punjab",
        "recommended_pesticides": ["Chlorantraniliprole"]
    }

    result = subsidy_finder_node(test_state)
    import json
    print(json.dumps(result, indent=2))
