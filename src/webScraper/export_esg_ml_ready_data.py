import json
import os
import sys
current_script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_script_dir)
E_OUTPUT_FILE = os.path.join(current_script_dir, "e.json")
S_OUTPUT_FILE = os.path.join(current_script_dir, "s.json")
G_OUTPUT_FILE = os.path.join(current_script_dir, "g.json")
sys.path.insert(0, parent_dir)
from databaseAccess.database import Database

def export_companies_to_json():
    db = Database()
    
    # Initialize separate outputs for E, S, G components
    e_output = []
    s_output = []
    g_output = []
    
    # Fetch all company documents
    for doc in db.companies_collection.find():
        company_id = str(doc.get("_id"))
        components = doc.get("esg_components", {})
        esg_score = doc.get("spglobal_esg_score")
        
        # Get E (Environmental) components
        e_texts = components.get("E", [])
        e_output.append({
            "company_id": company_id,
            "texts": e_texts,
            "esg_score": esg_score
        })
        
        # Get S (Social) components
        s_texts = components.get("S", [])
        s_output.append({
            "company_id": company_id,
            "texts": s_texts,
            "esg_score": esg_score
        })
        
        # Get G (Governance) components
        g_texts = components.get("G", [])
        g_output.append({
            "company_id": company_id,
            "texts": g_texts,
            "esg_score": esg_score
        })
    
    # Export E components to e.json
    e_json_data = json.dumps(e_output, indent=4)
    print("E (Environmental) data:")
    print(e_json_data)
    try:
        with open(E_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(e_json_data)
        print(f"Exported E components JSON to {E_OUTPUT_FILE}")
    except Exception as e:
        print(f"Failed to write E components export file: {e}")
    
    # Export S components to s.json
    s_json_data = json.dumps(s_output, indent=4)
    print("\nS (Social) data:")
    print(s_json_data)
    try:
        with open(S_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(s_json_data)
        print(f"Exported S components JSON to {S_OUTPUT_FILE}")
    except Exception as e:
        print(f"Failed to write S components export file: {e}")
    
    # Export G components to g.json
    g_json_data = json.dumps(g_output, indent=4)
    print("\nG (Governance) data:")
    print(g_json_data)
    try:
        with open(G_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(g_json_data)
        print(f"Exported G components JSON to {G_OUTPUT_FILE}")
    except Exception as e:
        print(f"Failed to write G components export file: {e}")

if __name__ == "__main__":
    export_companies_to_json()
