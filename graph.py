from typing import TypedDict, List, Dict, Optional, Any
from langgraph.graph import StateGraph, START, END

# --- IMPORT YOUR NODES ---
from image_analyzer import image_analyze_node
from pest_detector import pest_detector_node
from pesticide_finder import pesticide_finder_node
from sustainability_analyzer import sustainability_analyzer_node  # <-- NEW: Import Node E
from subsidy_finder import subsidy_finder_node

# ---------------------------------------------------------
# 1. STATE DEFINITION (The Shared Memory)
# ---------------------------------------------------------
class AgentState(TypedDict):
    
    # --- INPUTS ---
    image_path: str
    location: str
    month: str
    crop: str

    # --- NODE A & B ---
    candidate_analysis: Dict[str, str]
    confirmed_pest: Optional[str]    
    confidence_score: float           
    decision_reasoning: str           

    # --- NODE C: Pesticide Finder (Consolidated) ---
    # Now stores the full dictionaries containing category, dosage, and cost
    recommended_pesticides: List[Dict[str, Any]] 

    # --- NODE E: Sustainability Analyzer (NEW) ---
    environmental_impact_report: Optional[Dict[str, Any]]

    # --- NODE D: Subsidy Finder ---
    subsidy_info: List[Dict]         

    # --- ERROR TRACKING ---
    error: Optional[str]

# ---------------------------------------------------------
# 2. BUILD THE GRAPH
# ---------------------------------------------------------
workflow = StateGraph(AgentState)

# Add the 5 Nodes
workflow.add_node("image_analyzer", image_analyze_node)
workflow.add_node("pest_detector", pest_detector_node)
workflow.add_node("pesticide_finder", pesticide_finder_node)
workflow.add_node("sustainability_analyzer", sustainability_analyzer_node) # <-- NEW: Add Node E
workflow.add_node("subsidy_finder", subsidy_finder_node)

# ---------------------------------------------------------
# 3. DEFINE THE FLOW 
# ---------------------------------------------------------
workflow.add_edge(START, "image_analyzer")
workflow.add_edge("image_analyzer", "pest_detector")
workflow.add_edge("pest_detector", "pesticide_finder")

# <-- NEW: Insert Sustainability between Pesticide and Subsidy
workflow.add_edge("pesticide_finder", "sustainability_analyzer") 
workflow.add_edge("sustainability_analyzer", "subsidy_finder")

workflow.add_edge("subsidy_finder", END)

# ---------------------------------------------------------
# 4. COMPILE 
# ---------------------------------------------------------
app = workflow.compile()