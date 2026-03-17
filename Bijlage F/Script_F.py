import pandas as pd
import json
import glob
import os

def merge_tiktok_and_survey(json_folder, qualtrics_csv_path):
    all_respondents = []
    
    # 1. Verzamel data uit alle 'processed_*.json' bestanden
    json_files = glob.glob(os.path.join(json_folder, "processed_*.json"))
    for file_path in json_files:
        with open(file_path, 'r') as f:
            data = json.load(f)
            # Filter selective_exposure video's eruit voor de algoritmische analyse
            scores = [v['ideological_score'] for v in data['Watch_History'] if v.get('selective_exposure') is False]
            
            all_respondents.append({
                "Respondent_ID": data.get("Respondent_ID"),
                "total_videos": data['derived_variables'].get("total_videos"),
                "usage_intensity": data['derived_variables'].get("usage_intensity"),
                "pol_video_count": len(scores),
                "pol_video_scores": scores 
            })

    tiktok_df = pd.DataFrame(all_respondents)

    # 2. Laad Qualtrics data (we skippen de 2 metadata rijen van Qualtrics)
    survey_df = pd.read_csv(qualtrics_csv_path, low_memory=False).iloc[2:]

    # 3. Voer de Inner Join uit op de ID's
    master_df = pd.merge(tiktok_df, survey_df, left_on="Respondent_ID", right_on="ResponseId", how="inner")
    
    # 4. Gevoelige data verwijderen (Email Q18)
    if 'Q18' in master_df.columns:
        master_df = master_df.drop(columns=['Q18'])
    
    # Tussenstand opslaan
    master_df.to_pickle("master_intermediate.pkl")
    print(f"Koppeling gelukt! {len(master_df)} studenten in de dataset.")
    return master_df

# de . grijpt alle JSON files die beginnen met "processed_" in de huidige directory
# en qualtrics_data.csv is het bestand met de survey data
if __name__ == "__main__":
    merge_tiktok_and_survey(".", "qualtrics_data.csv")