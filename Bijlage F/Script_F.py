#################################################################################
#   Dit script is gebruikt om de survey-data te mergen met de TikTok-data       #
#                                                                               #
#################################################################################


import pandas as pd
import json
import glob
import os

def merge_tiktok_and_survey(json_folder, qualtrics_csv_path):
    all_respondents = []
    
    # verzamel data uit alle 'processed_*.json' bestanden
    json_files = glob.glob(os.path.join(json_folder, "processed_*.json"))
    for file_path in json_files:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
            # Alleen respondenten met 10000 of meer video's ---
            total_videos = data.get('derived_variables', {}).get("total_videos", 0)
            if total_videos < 10000:
                continue 
            
            scores = [v['ideological_score'] for v in data.get('Watch_History', [])]
            
            all_respondents.append({
                "Respondent_ID": data.get("Respondent_ID"),
                "total_videos": total_videos,
                "usage_intensity": data.get('derived_variables', {}).get("usage_intensity"),
                "pol_video_count": len(scores),
                "pol_video_scores": scores 
            })

    tiktok_df = pd.DataFrame(all_respondents)

    # Laad Qualtrics data (we skippen de 2 metadata rijen van Qualtrics)
    survey_df = pd.read_csv(qualtrics_csv_path, low_memory=False).iloc[2:]

    # Voer de Inner Join uit op de ID's
    master_df = pd.merge(tiktok_df, survey_df, left_on="Respondent_ID", right_on="ResponseId", how="inner")
    
    # Gevoelige data verwijderen (Email Q18)
    if 'Q18' in master_df.columns:
        master_df = master_df.drop(columns=['Q18'])
    
    # Tussenstand opslaan
    master_df.to_pickle("master_intermediate.pkl")
    print(f"Koppeling gelukt! {len(master_df)} studenten met 5000+ video's in de dataset.")
    
    return master_df

if __name__ == "__main__":
    # --- CONFIGURATIE ---
    # Zorg dat de map en het CSV bestand de juiste naam hebben
    df = merge_tiktok_and_survey("processed_data", "TikTok+Datadonatie_April+17,+2026_08.49.csv")
    
    if df is not None:
        print("\n--- CONTROLE PICKLE BESTAND ---")
        controle_df = pd.read_pickle("master_intermediate.pkl")
        aantal_rijen, aantal_kolommen = controle_df.shape
        print(f"✅ Het pickle bestand is succesvol geladen.")
        print(f"📊 Aantal studenten/respondenten (rijen): {aantal_rijen}")
        print(f"📈 Aantal variabelen/vragen (kolommen): {aantal_kolommen}")