# constants.py
from typing import List

VERIFICATION_DOMAINS = [
    "gov.in",
    "nic.in",
    "ac.in",           
    "vikaspedia.in",    
    "nbair.res.in",     
    "ncipm.org.in",    
    "org"              
]

PESTICIDE_DOMAINS = [
    "cibrc.nic.in",    
    "ppqs.gov.in",      
    "vikaspedia.in",   
    "ac.in",
    "agricoop.nic.in",
    "pau.edu"
]

CENTRAL_SUBSIDY_DOMAINS = [
    "myscheme.gov.in",       
    "pmkisan.gov.in",        
    "agriwelfare.gov.in",    
    "nfsm.gov.in",           
    "rkvy.nic.in",          
    "mkisan.gov.in"         
]

STATE_SUBSIDY_DOMAINS = {
   
    "Punjab": ["agri.punjab.gov.in", "punjab.gov.in"],
    "Haryana": ["agriharyana.gov.in"],
    "Uttar Pradesh": ["upagriculture.com", "agriculture.up.nic.in"],
    "Himachal Pradesh": ["agriculture.hp.gov.in"],
    "Uttarakhand": ["agriculture.uk.gov.in"],
    "Delhi": ["agri.delhi.gov.in"],
    
    
    "Rajasthan": ["agriculture.rajasthan.gov.in", "rajkisan.rajasthan.gov.in"],
    "Gujarat": ["agri.gujarat.gov.in", "ikhedut.gujarat.gov.in"],
    "Maharashtra": ["krishi.maharashtra.gov.in"],
    "Goa": ["agri.goa.gov.in"],
    
  
    "Karnataka": ["raitamitra.karnataka.gov.in"],
    "Tamil Nadu": ["tnagrisnet.tn.gov.in", "tnhorticulture.tn.gov.in"],
    "Andhra Pradesh": ["agri.ap.gov.in", "rythubharosa.ap.gov.in"],
    "Telangana": ["agri.telangana.gov.in", "rythubandhu.telangana.gov.in"],
    "Kerala": ["keralaagriculture.gov.in", "karshakasree.com"],
    
    
    "Bihar": ["krishi.bihar.gov.in", "farmech.bihar.gov.in"],
    "West Bengal": ["matirkatha.net", "wb.gov.in"],
    "Odisha": ["agri.odisha.gov.in", "kalia.odisha.gov.in"],
    "Jharkhand": ["agri.jharkhand.gov.in"],
    "Chhattisgarh": ["agriportal.cg.nic.in"],
    
   
    "Assam": ["diragri.assam.gov.in"],
    "Sikkim": ["sikkim.gov.in"],
    "Meghalaya": ["megagriculture.gov.in"],
    "Manipur": ["agrimanipur.mn.gov.in"],
    "Mizoram": ["agriculturemizoram.nic.in"],
    "Nagaland": ["agriculture.nagaland.gov.in"],
    "Tripura": ["agri.tripura.gov.in"],
    "Arunachal Pradesh": ["agri.arunachal.gov.in"]
}

def get_subsidy_domains(user_state: str) -> List[str]:
    """
    Returns the list of domains to search for subsidies.
    Combines CENTRAL domains with the specific STATE domain.
    """
    
    allowed_domains = CENTRAL_SUBSIDY_DOMAINS.copy()
    
    if not user_state:
        return allowed_domains

    
    clean_state = user_state.strip().title()
    
   
    if clean_state in STATE_SUBSIDY_DOMAINS:
        specific_domains = STATE_SUBSIDY_DOMAINS[clean_state]
        allowed_domains.extend(specific_domains)
        
    return allowed_domains