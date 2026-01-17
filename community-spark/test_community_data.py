"""
Test script for community data lookup
"""

from app.data.community_data import lookup_community_metrics

# Test with zip code
print("=" * 60)
print("Testing Community Data Lookup")
print("=" * 60)

# Test 1: Zip code lookup
print("\n1. Testing with zip code:")
profile1 = {"zip_code": "10451"}
metrics1 = lookup_community_metrics(profile1)
print(f"   Zip: {profile1['zip_code']}")
print(f"   Low income area: {metrics1['low_income_area']}")
print(f"   Food desert: {metrics1['food_desert']}")
print(f"   Local hiring rate: {metrics1['local_hiring_rate']}")
print(f"   Nearest grocery: {metrics1['nearest_grocery_miles']} miles")

# Test 2: Lat/lon lookup (will use defaults since no bucket match)
print("\n2. Testing with lat/lon:")
profile2 = {"latitude": 40.7589, "longitude": -73.9851}
metrics2 = lookup_community_metrics(profile2)
print(f"   Location: {profile2['latitude']}, {profile2['longitude']}")
print(f"   Low income area: {metrics2['low_income_area']}")
print(f"   (Using defaults - no bucket match)")

# Test 3: No location data (defaults)
print("\n3. Testing with no location:")
profile3 = {"name": "Test Business"}
metrics3 = lookup_community_metrics(profile3)
print(f"   (No location provided)")
print(f"   Using defaults: low_income_area={metrics3['low_income_area']}")

# Test 4: Different zip code
print("\n4. Testing different zip code:")
profile4 = {"zip_code": "33139"}
metrics4 = lookup_community_metrics(profile4)
print(f"   Zip: {profile4['zip_code']}")
print(f"   Low income area: {metrics4['low_income_area']}")
print(f"   Food desert: {metrics4['food_desert']}")
print(f"   Local hiring rate: {metrics4['local_hiring_rate']}")

print("\n" + "=" * 60)
print("✓ All tests complete!")

