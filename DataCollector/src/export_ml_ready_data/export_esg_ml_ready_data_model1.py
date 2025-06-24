import json
import os
import sys
current_script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_script_dir)
OUTPUT_FILE = os.path.join(current_script_dir, "../../../ML/ml_ready_data/ml_ready_esg_data_model1.json")
sys.path.insert(0, parent_dir)
from databaseAccess.database import Database

def export_companies_to_json():
    db = Database()
    #db.add_company("Test Company", "TEST")
    output = []
    # Fetch all company documents
    for doc in db.companies_collection.find():
        company_id = str(doc.get("_id"))
        components = doc.get("esg_components", {})
        # Combine E, S, G texts
        texts = []
        for cat in ["E", "S", "G"]:
            texts.extend(components.get(cat, []))
        esg_score = doc.get("spglobal_esg_score")
        if esg_score is None:
            continue  # Skip if ESG score is not available
        output.append({
            "company_id": company_id,
            "texts": texts,
            "esg_score": float(esg_score)
        })
    json_data = json.dumps(output, indent=4)
    print(json_data)
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(json_data)
        print(f"Exported JSON to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Failed to write export file: {e}")

if __name__ == "__main__":
    export_companies_to_json()
