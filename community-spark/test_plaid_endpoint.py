"""
Test script for /evaluate/plaid endpoint

This demonstrates the full flow with Plaid integration.
"""

import asyncio
import httpx


async def test_plaid_endpoint():
    """Test the /evaluate/plaid endpoint"""
    print("=" * 60)
    print("Testing /evaluate/plaid Endpoint")
    print("=" * 60)
    
    # Sample business profile
    business_profile = {
        "type": "retail",
        "low_income_area": True,
        "nearest_competitor_miles": 8,
        "hires_locally": True,
        "name": "Community Market",
        "industry": "grocery"
    }
    
    print("\nSending request with business_profile:")
    print(f"  Type: {business_profile['type']}")
    print(f"  Low-income area: {business_profile['low_income_area']}")
    print(f"  Competitor distance: {business_profile['nearest_competitor_miles']} miles")
    print(f"  Hires locally: {business_profile['hires_locally']}")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            print("\nCalling API (this may take a few seconds)...")
            response = await client.post(
                "http://127.0.0.1:8000/evaluate/plaid",
                json={"business_profile": business_profile}
            )
            response.raise_for_status()
            result = response.json()
        
        print("\n" + "=" * 60)
        print("✓ Success! Evaluation Complete")
        print("=" * 60)
        
        print(f"\nFinal Decision: {result.get('final_decision')}")
        print(f"Auditor Score: {result.get('auditor_score')}")
        print(f"Community Multiplier: {result.get('community_multiplier')}")
        print(f"Used Plaid: {result.get('used_plaid')}")
        
        print(f"\nDecision Rationale:")
        print(f"  {result.get('decision_rationale')}")
        
        if result.get('loan_terms'):
            print(f"\nLoan Terms:")
            for key, value in result['loan_terms'].items():
                print(f"  {key}: {value}")
        
        print(f"\nExtracted Features from Plaid:")
        features = result.get('extracted_features', {})
        for key, value in features.items():
            print(f"  {key}: {value}")
        
        print(f"\nWorkflow Log ({len(result.get('log', []))} steps):")
        for entry in result.get('log', []):
            print(f"  [{entry['agent']}] {entry['message']}")
        
    except httpx.HTTPStatusError as e:
        print(f"\n✗ HTTP Error: {e}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure:")
        print("1. Server is running: uvicorn app.main:app --reload")
        print("2. PLAID_CLIENT_ID and PLAID_SECRET are set")


if __name__ == "__main__":
    asyncio.run(test_plaid_endpoint())

