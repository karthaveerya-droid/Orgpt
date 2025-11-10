"""
swagger_connector.py
---------------------
Main runner for Orgpt Swagger ingestion.
Fetches Swagger/OpenAPI specs from URLs and prints parsed endpoint info.
"""

from ingestion.swagger_connector_helpers import (
    fetch_swagger,
    extract_full_api_spec,
    render_api_to_text,
)
import traceback

if __name__ == "__main__":
    # 🔹 Public Swagger sources for testing
    swaggers = {
        "Petstore": "https://petstore.swagger.io/v2/swagger.json",
        "Weather.gov": "https://api.weather.gov/openapi.json",
        "Swagger.io Generator": "https://generator.swagger.io/api/swagger.json",
    }

    for name, url in swaggers.items():
        print(f"\n{'='*80}")
        print(f" Testing {name}: {url}")
        print(f"{'='*80}")
        try:
            spec = fetch_swagger(url)
            api_info = extract_full_api_spec(spec)
            docs = render_api_to_text(api_info)

            print(f" Extracted {len(api_info['paths'])} endpoints.")
            print(f"Sample Output:\n{'-'*60}")
            for d in docs[:3]:
                print(d[:800])
                print('-'*60)
        except Exception as e:
            print(f"Failed for {name}: {e}")
            traceback.print_exc()
