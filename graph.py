from typing import TypedDict, List, Dict, Optional, Any
from langgraph.graph import StateGraph, START, END

from image_analyzer import image_analyze_node
from pest_detector import pest_detector_node
from pesticide_finder import pesticide_finder_node
from subsidy_finder import subsidy_finder_node

class AgentState(TypedDict):
    
    image_path: str
    location: str
    month: str
    crop: str

    candidate_analysis: Dict[str, str]

    confirmed_pest: Optional[str]    
    confidence_score: float           
    decision_reasoning: str           

    recommended_pesticides: List[str] 
    detailed_pesticide_info: List[Dict] 

    subsidy_info: List[Dict]         

    error: Optional[str]

workflow = StateGraph(AgentState)

# Add the 4 Nodes
workflow.add_node("image_analyzer", image_analyze_node)
workflow.add_node("pest_detector", pest_detector_node)
workflow.add_node("pesticide_finder", pesticide_finder_node)
workflow.add_node("subsidy_finder", subsidy_finder_node)


workflow.add_edge(START, "image_analyzer")
workflow.add_edge("image_analyzer", "pest_detector")
workflow.add_edge("pest_detector", "pesticide_finder")
workflow.add_edge("pesticide_finder", "subsidy_finder")
workflow.add_edge("subsidy_finder", END)

app = workflow.compile()

