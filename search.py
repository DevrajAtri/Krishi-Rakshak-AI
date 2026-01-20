import os
from typing import List, Dict, Optional
from langchain_community.tools.tavily_search import TavilySearchResults


def search_web(query: str, max_results: int = 3, domains: Optional[List[str]] = None) -> List[Dict]:
    """
    Executes a web search optimized for LLM consumption.
    
    Args:
        query (str): The search string.
        max_results (int): How many sources to return.
        domains (List[str]): Optional list of domains to restrict search to (e.g., ["gov.in"]).
    
    Returns:
        List[Dict]: A list of results containing 'url' and 'content'.
    """
    
    if domains:
        domain_str = " OR ".join([f"site:{d}" for d in domains])
        final_query = f"{query} {domain_str}"
    else:
        final_query = query

    print(f"    🔍 Searching: '{final_query}'")

    try:
        
        tool = TavilySearchResults(max_results=max_results)
        
        results = tool.invoke({"query": final_query})
        
        clean_results = []
        for res in results:
            clean_results.append({
                "url": res.get("url"),
                "content": res.get("content", "")[:500]
            })
            
        return clean_results

    except Exception as e:
        print(f"    ❌ Search Error: {e}")
        return []

def format_search_results(results: List[Dict]) -> str:
    """Helper to turn list of dicts into a single string for the Prompt."""
    if not results:
        return "No search results found."
        
    formatted = ""
    for i, res in enumerate(results, 1):
        formatted += f"Source {i}:\nURL: {res['url']}\nContent: {res['content']}\n\n"
    return formatted


if __name__ == "__main__":
    # Test 1: General Search
    print("--- Test 1: General Search ---")
    res1 = search_web("symptoms of Fall Armyworm in Maize")
    print(format_search_results(res1))
    
    # Test 2: Targeted Government Search
    print("\n--- Test 2: Gov Search ---")
    res2 = search_web("subsidy for solar pump", domains=["gov.in"])
    print(format_search_results(res2))