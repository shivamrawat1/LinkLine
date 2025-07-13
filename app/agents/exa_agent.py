import google.generativeai as genai
from exa_py import Exa
from exa_py.websets.types import CreateWebsetParameters, CreateEnrichmentParameters
from dotenv import load_dotenv
import os
import json
import time
import asyncio

def setup_gemini():
    """Setup Gemini API"""
    print("Setting up Gemini API")
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash')

def process_study_description(description):
    """Use Gemini to extract a search query from a study description"""
    if not description:
        raise ValueError("Study description cannot be None or empty")
    
    model = setup_gemini()

    prompt = f"""
    You are an AI assistant that helps researchers find participants for their studies. 
    Given the following research study description, generate a concise search query 
    that can be used to find relevant participants.

    Focus only on returning a single-line search query based on:
    - Professional roles or job titles
    - Industry or domain
    - Skills or expertise
    - Demographics (e.g. location, education level, etc.)

    Study Description: {description}

    Only return the search query. Do not include explanations or any other text.
    """

    try:
        response = model.generate_content(prompt)
        search_query = response.text.strip()
        print(f"Search Query: {search_query}")
        return search_query
    
    except Exception as e:
        print(f"Error generating search query: {e}")
        return "biology college students in San Francisco"


def search_participants(study_description):
    """Search for potential participants using Exa Websets API (synchronous)"""
    load_dotenv()
    print(os.getenv('EXA_API_KEY'))
    
    # Check if API key is available
    api_key = os.getenv('EXA_API_KEY')
    print(api_key)
    if not api_key:
        raise ValueError("EXA_API_KEY not found in environment variables")
    
    exa = Exa(api_key)
    
    # Process the study description using Gemini
    search_query = process_study_description(study_description)
    
    print(f"Searching with query: {search_query}")

    webset = exa.websets.create(
        params=CreateWebsetParameters(
            search={
                "query": search_query,
                "count": 5
            },
            enrichments=[
                CreateEnrichmentParameters(
                    description="Email of the person",
                    format="email",
                ),
                CreateEnrichmentParameters(
                    description="Phone of number of the person",
                    format="phone",
                ),
            ],
        )
    )

    # Wait for processing to complete
    webset = exa.websets.wait_until_idle(webset.id)

    # Retrieve and parse items
    items = exa.websets.items.list(webset_id=webset.id)
    output = []

    for item in items.data:
        # Safely access person object
        person = getattr(item.properties, "person", None)
        name = str(getattr(person, "name", "")) if person else "Unknown"

        # Safely access URL (AnyUrl needs to be cast to string)
        raw_url = getattr(item.properties, "url", None)
        url = str(raw_url) if raw_url else None

        # Extract email and phone
        email = None
        phone = None
        for enrichment in item.enrichments:
            if enrichment.format == "email" and enrichment.result:
                # Handle different result types
                if isinstance(enrichment.result, list) and len(enrichment.result) > 0:
                    email = enrichment.result[0]
                elif isinstance(enrichment.result, str):
                    email = enrichment.result
            elif enrichment.format == "phone" and enrichment.result:
                # Handle different result types for phone
                if isinstance(enrichment.result, list) and len(enrichment.result) > 0:
                    phone = enrichment.result[0]
                elif isinstance(enrichment.result, str):
                    phone = enrichment.result

        output.append({
            "name": name,
            "email": email or "Not found",
            "phone": phone or "Not found",
            "linkedin": url or "Not found"
        })

    return {
        "participants": output,
        "total_results": len(output)
    }




