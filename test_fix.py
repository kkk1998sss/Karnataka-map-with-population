#!/usr/bin/env python3
"""
Quick test to regenerate data and verify field names
"""

def main():
    print("🔄 Testing data regeneration with proper field names...")
    
    try:
        # Try to generate the complete Karnataka map
        from karnataka_map_generator import generate_karnataka_map
        print("🗺️ Generating complete Karnataka map...")
        map_data = generate_karnataka_map()
        
        # Check the first village feature
        if len(map_data['features']) > 1:  # First feature is state boundary
            first_village = map_data['features'][1]  # Second feature should be a village
            props = first_village['properties']
            
            print("\n✅ First village properties:")
            print(f"   State Name: {props.get('state_name', 'MISSING')}")
            print(f"   Village Name: {props.get('village_na', 'MISSING')}")
            print(f"   District: {props.get('district_n', 'MISSING')}")
            print(f"   Subdistrict: {props.get('subdistric', 'MISSING')}")
            print(f"   Census ID: {props.get('pc11_tv_id', 'MISSING')}")
            print(f"   Population: {props.get('tot_p', 'MISSING')}")
            
            # Verify all required fields are present
            required_fields = ['state_name', 'village_na', 'district_n', 'subdistric', 'pc11_tv_id', 'tot_p']
            missing_fields = [field for field in required_fields if field not in props or not props[field]]
            
            if missing_fields:
                print(f"\n❌ Missing or empty fields: {missing_fields}")
            else:
                print(f"\n✅ All required fields are present and populated!")
                
        else:
            print("❌ No village features found in generated data")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("🔧 Trying simple data loader...")
        
        try:
            from simple_data_loader import create_sample_data
            sample_data = create_sample_data()
            
            if len(sample_data['features']) > 0:
                first_village = sample_data['features'][0]
                props = first_village['properties']
                
                print("\n✅ Simple data first village properties:")
                print(f"   State Name: {props.get('state_name', 'MISSING')}")
                print(f"   Village Name: {props.get('village_na', 'MISSING')}")
                print(f"   District: {props.get('district_n', 'MISSING')}")
                print(f"   Subdistrict: {props.get('subdistric', 'MISSING')}")
                print(f"   Census ID: {props.get('pc11_tv_id', 'MISSING')}")
                print(f"   Population: {props.get('tot_p', 'MISSING')}")
            else:
                print("❌ No features in simple data")
                
        except Exception as e2:
            print(f"❌ Simple data also failed: {e2}")

if __name__ == "__main__":
    main()
