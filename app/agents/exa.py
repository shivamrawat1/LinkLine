from exa_py import Exa
from dotenv import load_dotenv
from exa_py.websets.types import CreateWebsetParameters, CreateEnrichmentParameters
import os
import json

def main():
    load_dotenv()
    exa = Exa(os.getenv('EXA_API_KEY'))

    # Create a Webset with search and enrichments
    webset = exa.websets.create(
        params=CreateWebsetParameters(
            search={
                "query": "Participants must be currently enrolled in college and studying biology or a related field and based in San Francisco during the study period.",
                "count": 6
            },
            enrichments=[
                CreateEnrichmentParameters(
                    description="Email of the person",
                    format="email",
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
        name = str(getattr(person, "name", "")) if person else None

        # Safely access URL (AnyUrl needs to be cast to string)
        raw_url = getattr(item.properties, "url", None)
        url = str(raw_url) if raw_url else None

        # Extract email
        email = None
        for enrichment in item.enrichments:
            if enrichment.format == "email" and enrichment.result:
                email = enrichment.result[0]
                break

        output.append({
            "name": name,
            "email": email,
            "linkedin": url
        })

    # Print JSON output
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
