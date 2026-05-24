import json
from datetime import datetime
import os

# functie om de TikTokdata te verwerken (Selective Exposure check verwijderd)
def process_tiktok_data(respondent_json_path, library_json_path, output_dir):
    print(f"--- Start verwerking: {respondent_json_path} ---")
    
    with open(library_json_path, 'r') as f:
        library = json.load(f)
    
    party_scores = {
        "BIJ1": 99,       # Not in dataset
        "PvdD": 1.5,      # CHES: 1.5
        "SP": 1.2,        # CHES: 1.17
        "GL-PvdA": 2.8,   # Average of GL (2.5) and PvdA (3.0)
        "Volt": 4.5,      # CHES: 4.55
        "DENK": 3.9,      # CHES: 3.89
        "D66": 4.7,       # CHES: 4.67
        "50PLUS": 99,     # Not in dataset
        "NSC": 6.6,       # CHES: 6.58
        "CDA": 5.8,       # CHES: 5.75
        "VVD": 7.7,       # CHES: 7.67
        "BBB": 7.8,       # CHES: 7.75
        "JA21": 99,       # Not in dataset
        "PVV": 9.1,       # CHES: 9.08
        "FvD": 9.8        # CHES: 9.83
    }

    # Maak lookup: video_id -> {party, creator, score}
    video_lookup = {}
    for party, accounts in library.items():
        score = party_scores.get(party)
        for creator_handle, video_ids in accounts.items():
            for vid in video_ids:
                video_lookup[vid] = {
                    "party": party, 
                    "creator": creator_handle, 
                    "ideological_score": score
                }

    # 2. Laad Respondent Data
    with open(respondent_json_path, 'r') as f:
        res_data = json.load(f)
    
    watch_history = res_data.get("Watch History", [])
    res_id = res_data.get("Respondent_ID")

    # Als de ID per ongeluk ontbreekt, haal hem uit de bestandsnaam
    if not res_id:
        filename = os.path.basename(respondent_json_path)
        res_id = filename.replace("_tiktok_data.json", "")

    # 3. Stap 1: Identificeer politieke video's uit de bibliotheek
    for video in watch_history:
        # Check of de short_link daadwerkelijk bestaat om errors te voorkomen
        if 'short_link' in video and video['short_link']:
            video_id = video['short_link'].strip('/').split('/')[-1]
            match = video_lookup.get(video_id)
            
            if match:
                video['is_political'] = True
                video['creator'] = match['creator']
                video['party'] = match['party']
                video['ideological_score'] = match['ideological_score']
            else:
                video['is_political'] = False
                video['creator'] = None
                video['ideological_score'] = None
        else:
            video['is_political'] = False
            video['creator'] = None
            video['ideological_score'] = None

    # 5. Gebruiksintensiteit (GEFIXT: Voorkomt crash bij lege data)
    if watch_history:
        dates = [datetime.strptime(v['date'], '%Y-%m-%d %H:%M:%S') for v in watch_history if 'date' in v]
        if dates:
            days_diff = (max(dates) - min(dates)).days + 1
            usage_intensity = len(watch_history) / days_diff
        else:
            usage_intensity = 0
    else:
        usage_intensity = 0

    # alleen politieke video's overhouden
    political_only = [v for v in watch_history if v.get('is_political')]
    
    final_output = {
        "Respondent_ID": res_id,
        "derived_variables": {
            "total_videos": len(watch_history),
            "usage_intensity": round(usage_intensity, 2)
        },
        "Watch_History": political_only
    }

    # Opslaan in de nieuwe map
    output_name = f"processed_{res_id}.json"
    output_path = os.path.join(output_dir, output_name)
    
    with open(output_path, 'w') as f:
        json.dump(final_output, f, indent=4)
    
    print(f"Resultaat staat in {output_path}")

if __name__ == "__main__":
    # Configuratie
    INPUT_DIR = "scriptie-datadonatie-2025"   # Map met de R_... bestanden
    OUTPUT_DIR = "processed_data"             # Map voor de output
    LIB = "tiktok_library.json"               # Zorg dat deze in dezelfde directory staat
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if os.path.exists(INPUT_DIR):
        for filename in os.listdir(INPUT_DIR):
            if filename.startswith("R_") and filename.endswith(".json"):
                input_file_path = os.path.join(INPUT_DIR, filename)
                process_tiktok_data(input_file_path, LIB, OUTPUT_DIR)
                
        print("\nAlle respondenten zijn succesvol verwerkt!")
    else:
        print(f"Fout: De map '{INPUT_DIR}' kon niet worden gevonden.")