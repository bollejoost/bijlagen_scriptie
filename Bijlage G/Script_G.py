#################################################################################
#   Dit script is gebruikt om de gemergde dataset om te zetten in een .CSV      #
#   en de basisvariabelen te berekenen                                          #
#################################################################################


import pandas as pd
import numpy as np
import json
import random

def calculate_final_variables(pickle_path, library_json_path):
    # Inladen data
    df = pd.read_pickle(pickle_path)

    # CHES scores 2024 
    ches_scores = {
        "BIJ1": 99,       "PvdD": 1.5,      "SP": 1.2, 
        "GL-PvdA": 2.8,   "Volt": 4.6,      "DENK": 3.9, 
        "D66": 4.7,       "CU": 4.6,        "NSC": 6.6, 
        "CDA": 5.8,       "VVD": 7.7,       "BBB": 7.8, 
        "SGP": 8.0,       "JA21": 99,       "PVV (Unofficial)": 9.1, 
        "FvD": 9.8,       "50PLUS": 99
    }

    with open(library_json_path, 'r') as f:
        library = json.load(f)
    
    # Baseline pool (alleen voor partijen met echte CHES score)
    all_possible_scores = []
    for party, creators in library.items():
        score = ches_scores.get(party)
        if score is not None and score != 99:
            for creator, vids in creators.items():
                all_possible_scores.extend([score] * len(vids))

    # Partij-mapping Qualtrics
    party_mapping = {
        "1": "PVV (Unofficial)", "2": "GL-PvdA", "3": "VVD", "4": "NSC", "5": "D66",
        "6": "BBB", "7": "CDA", "8": "SP", "9": "DENK", "10": "PvdD",
        "11": "FvD", "12": "SGP", "13": "CU", "14": "Volt",
        "15": "JA21", "16": "BIJ1", "17": "Anders"
    }

    # Transformaties
    df['Q17'] = pd.to_numeric(df['Q17'], errors='coerce')
    df = df[df['Q17'].isin([1, 3])].copy() 

    df['age'] = pd.to_numeric(df['Q15'], errors='coerce') + 17
    df['political_identity_self'] = pd.to_numeric(df['Q10_1'], errors='coerce')
    
    df['political_identity_party_raw'] = df['Q14'].astype(str).map(party_mapping).map(ches_scores)
    df['political_identity_party'] = df['political_identity_party_raw'].copy()
    df.loc[df['political_identity_party'] == 99, 'political_identity_party'] = df['political_identity_self']
    
    df['political_identity_index'] = df[['political_identity_self', 'political_identity_party']].mean(axis=1)

    # Berekening van statistieken
    def run_simulations_and_stats(row):
        raw_scores = row['pol_video_scores']
        identity = row['political_identity_index']
        self_id = row['political_identity_self']
        
        if not isinstance(raw_scores, list) or pd.isna(identity) or pd.isna(self_id):
            return pd.Series([None, None, None, None, None])

        scores = []
        for s in raw_scores:
            if isinstance(s, (int, float)) and not pd.isna(s):
                # AANGEPAST: Score wordt alleen toegevoegd als deze NIET 99 is
                if s != 99:
                    scores.append(s)
        
        n = len(scores)
        if n == 0:
            return pd.Series([None, None, None, None, None])

        median_score = np.median(scores)
        mean_score = np.mean(scores)
        observed_alignment = np.mean([abs(s - identity) for s in scores])
        
        simulated_distances = []
        for _ in range(1000):
            random_sample = random.sample(all_possible_scores, n)
            sim_dist = np.mean([abs(s - identity) for s in random_sample])
            simulated_distances.append(sim_dist)
        
        random_baseline_alignment = np.mean(simulated_distances)
        personalization_score = random_baseline_alignment - observed_alignment
        diversity = np.std(scores) if n > 1 else 0
        
        return pd.Series([median_score, mean_score, observed_alignment, personalization_score, diversity])

    df[['ideological_median', 'ideological_mean', 'ideological_alignment', 'personalization_score', 'ideological_diversity']] = df.apply(run_simulations_and_stats, axis=1)

    # Overige variabelen
    df['political_exposure'] = df['pol_video_count'] / df['total_videos'].astype(float)
    df['political_interest'] = pd.to_numeric(df['Q13_1'], errors='coerce')

    print("\n--- CHECK: IMPACT PARTIJEN ZONDER CHES-SCORE ---")
    
    totaal_99_gezien = 0
    totaal_politiek_gezien = 0
    
    for vid_list in df['pol_video_scores']:
        if isinstance(vid_list, list):
            totaal_99_gezien += vid_list.count(99)
            totaal_politiek_gezien += len(vid_list)
            
    aantal_respondenten = len(df)
    percentage = (totaal_99_gezien / totaal_politiek_gezien * 100) if totaal_politiek_gezien > 0 else 0
    
    print(f"Totaal politieke video's geanalyseerd (alle respondenten): {totaal_politiek_gezien}")
    print(f"Waarvan video's zonder CHES-score (BIJ1/JA21/50PLUS):  {totaal_99_gezien}")
    print(f"Percentage placeholder-video's:                      {percentage:.2f}%")
    
    if aantal_respondenten > 0:
        print(f"Gemiddelde per respondent:                           {totaal_99_gezien / aantal_respondenten:.2f} video's")
    
    print("--------------------------------------------------------\n")

    # Export
    final_cols = [
        'Respondent_ID', 'age', 'Q16', 'total_videos',
        'political_identity_self', 'political_identity_party', 'political_identity_index', 
        'political_interest', 'ideological_median', 'ideological_mean', 'ideological_alignment', 
        'personalization_score', 'ideological_diversity', 'political_exposure', 'usage_intensity'
    ]
    
    df_final = df[final_cols].rename(columns={'Q16': 'gender'}).dropna(subset=['ideological_alignment'])
    df_final.to_csv("master_dataset_test.csv", index=False)
    print(f"✅ Klaar! Dataset opgeslagen met {len(df_final)} respondenten.")

if __name__ == "__main__":
    calculate_final_variables("master_intermediate.pkl", "tiktok_library.json")