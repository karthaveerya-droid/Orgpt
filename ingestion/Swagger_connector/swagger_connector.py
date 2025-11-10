"""
swagger_connector.py
---------------------
Upgraded ingestion for Orgpt.
Fetches multiple Swagger/OpenAPI sources and returns a single list of flattened text docs.
Drop-in compatible with main.py expecting: docs = extract_text_from_swagger(...)
"""

from ingestion.Swagger_connector.swagger_connector_helpers import (
    fetch_swagger,
    extract_full_api_spec,
    render_api_to_text,
)

def extract_text_from_swagger_sources():
    """
    Fetch multiple Swagger/OpenAPI sources and return a single list of text docs.
    """
    sources = {
        "Petstore": "https://petstore.swagger.io/v2/swagger.json",
        "Weather.gov": "https://api.weather.gov/openapi.json",
        "Swagger.io Generator": "https://generator.swagger.io/api/swagger.json",
    }

    all_docs = []

    for name, url in sources.items():
        print("\n" + "="*80)
        print(f"Testing {name}: {url}")
        print("="*80)

        try:
            spec = fetch_swagger(url)
            api_info = extract_full_api_spec(spec)
            docs = render_api_to_text(api_info)
            all_docs.extend(docs)

            print(f"Extracted {len(api_info.get('paths', []))} endpoints from {api_info.get('title', name)}")
            print(f"Sample Output:\n{'-'*60}")
            for d in docs[:2]:
                print(d[:400])
                print('-'*60)

        except Exception as e:
            print(f"❌ Failed for {name}: {e}")

    return all_docs


# ---------- CLI / Local Testing ----------

if __name__ == "__main__":
    docs = extract_text_from_swagger_sources()

    print("\n" + "="*80)
    print("✅ Summary")
    print("="*80)
    print(f"Total text docs: {len(docs)}")
