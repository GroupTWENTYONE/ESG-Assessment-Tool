import json
import os
import sys
current_script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_script_dir)
E_OUTPUT_FILE = os.path.join(current_script_dir, "../../../ML/ml_ready_data/ml_ready_e.jsonlines")
S_OUTPUT_FILE = os.path.join(current_script_dir, "../../../ML/ml_ready_data/ml_ready_s.jsonlines")
G_OUTPUT_FILE = os.path.join(current_script_dir, "../../../ML/ml_ready_data/ml_ready_g.jsonlines")
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
        individual_scores = doc.get("spglobal_individual_scores", {})
        esg_score = doc.get("spglobal_esg_score")

        if not components or esg_score is None:
            print(f"Skipping company {company_id} due to missing components or ESG score.")
            continue
        
        # Get E (Environmental) components
        e_texts = components.get("E", [])
        e_score = individual_scores.get("environmental", int)  # Use individual score if available
        e_output.append({
            "id": company_id,
            "text": " ".join(e_texts[2:3]),
            "score": int(e_score)
        })
        
        # Get S (Social) components
        s_texts = components.get("S", [])
        s_score = individual_scores.get("social", int)  # Use individual score if available
        s_output.append({
            "id": company_id,
            "text": " ".join(s_texts),
            "score": int(s_score)
        })
        
        # Get G (Governance) components
        g_texts = components.get("G", [])
        g_score = individual_scores.get("governance", int)  # Use individual score if available
        g_output.append({
            "id": company_id,
            "text": " ".join(g_texts),
            "score": int(g_score)
        })
    
    # Export E components to e.json
    e_json_data = json.dumps(e_output, indent=4)
    print("E (Environmental) data:")
    print(e_json_data)
    try:
        with open(E_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            for item in e_output:
                json_line = json.dumps(item, ensure_ascii=False, separators=(',', ':'))
                f.write(json_line + '\n')
            #f.write(e_json_data)
        print(f"Exported E components JSON to {E_OUTPUT_FILE}")
    except Exception as e:
        print(f"Failed to write E components export file: {e}")
    
    # Export S components to s.json
    s_json_data = json.dumps(s_output, indent=4)
    print("\nS (Social) data:")
    print(s_json_data)
    try:
        with open(S_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            for item in s_output:
                json_line = json.dumps(item, ensure_ascii=False, separators=(',', ':'))
                f.write(json_line + '\n')
            #f.write(s_json_data)
        print(f"Exported S components JSON to {S_OUTPUT_FILE}")
    except Exception as e:
        print(f"Failed to write S components export file: {e}")
    
    # Export G components to g.json
    g_json_data = json.dumps(g_output, indent=4)
    print("\nG (Governance) data:")
    print(g_json_data)
    try:
        with open(G_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            for item in g_output:
                json_line = json.dumps(item, ensure_ascii=False, separators=(',', ':'))
                f.write(json_line + '\n')
            #f.write(g_json_data)
        print(f"Exported G components JSON to {G_OUTPUT_FILE}")
    except Exception as e:
        print(f"Failed to write G components export file: {e}")

if __name__ == "__main__":
    export_companies_to_json()
