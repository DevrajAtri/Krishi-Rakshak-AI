from typing import TypedDict, Dict, List, Optional

class AgentState(TypedDict):
    
    image_path: str
    location: str       # e.g., "Punjab"
    month: str          # e.g., "October"
    crop : str          # e.g wheat 
    
    candidate_analysis: Dict[str, str] 
    
    confirmed_pest: Optional[str]  
    confidence_score: float         
    
    recommended_pesticides: List[str] 
    subsidy_info: Dict[str, str]  
    
    # --- FLAGS ---
    error: Optional[str]    

    environmental_impact_report: Optional[Dict]        