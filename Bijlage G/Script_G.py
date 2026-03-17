import pandas as pd
import numpy as np
import json
import random

def calculate_final_variables(pickle_path, library_json_path):
    df = pd.read_pickle(pickle_path)

    # 1. CHES scores en Random Baseline
    with open(library_json_path, 'r') as f:
        library = json.load(f)
    
    ches_scores = {
        "BIJ1": 0.5, "PvdD": 1.2, "SP": 1.8, "GL-PvdA": 2.2, "Volt": 3.8, 
        "DENK": 4.2, "D66": 4.8, "ChristenUnie": 5.1, "NSC": 6.2, "CDA": 6.4, 
        "VVD": 7.8, "BBB": 8.1, "JA21": 8.9, "SGP": 9.1, "PVV": 9.3, "FvD": 9.8
    }

    all_possible_scores = []
    for party, creators in library.items():
        score = ches_scores.get(party)
        if score is not None:
            for creator, vids in creators.items():
                all_possible_scores.extend([score] * len(vids))

    # 2. Partij-mapping Qualtrics 
    party_mapping = {
        "1": "PVV", "2": "GL-PvdA", "3": "VVD", "4": "NSC", "5": "D66",
        "6": "BBB", "7": "CDA", "8": "SP", "9": "DENK", "10": "PvdD",
        "11": "FvD", "12": "SGP", "13": "ChristenUnie", "14": "Volt",
        "15": "JA21", "16": "BIJ1", "17": "Anders"
    }

    # 3. Transformaties & Indexen
    df['Q17'] = pd.to_numeric(df['Q17'], errors='coerce')
    df = df[df['Q17'].isin([1, 3])].copy() # Filter studenten

    df['age'] = pd.to_numeric(df['Q15'], errors='coerce') + 17
    df['political_identity_self'] = pd.to_numeric(df['Q10_1'], errors='coerce')
    df['political_identity_party'] = df['Q14'].astype(str).map(party_mapping).map(ches_scores)
    df['political_identity_index'] = df[['political_identity_self', 'political_identity_party']].mean(axis=1)

    # 4. Berekening van statistieken per respondent (inclusief Simulatie)
    def run_simulations_and_stats(row):
        scores = row['pol_video_scores']
        identity = row['political_identity_index']
        n = len(scores)
        
        if n == 0 or pd.isna(identity):
            return pd.Series([None, None, None, None, None])

        # A. Mediaan en Gemiddelde van de feed
        median_score = np.median(scores)
        mean_score = np.mean(scores)
        
        # B. Werkelijke afstemming (Observed Alignment)
        observed_alignment = np.mean([abs(s - identity) for s in scores])
        
        # C. Random Baseline Simulatie (1000 runs)
        simulated_distances = []
        for _ in range(1000):
            random_sample = random.sample(all_possible_scores, n)
            sim_dist = np.mean([abs(s - identity) for s in random_sample])
            simulated_distances.append(sim_dist)
        
        random_baseline_alignment = np.mean(simulated_distances)
        personalization_score = random_baseline_alignment - observed_alignment
        diversity = np.std(scores) if n > 1 else 0
        
        return pd.Series([median_score, mean_score, observed_alignment, personalization_score, diversity])

    # Toepassen op de dataset
    df[['ideological_median', 'ideological_mean', 'ideological_alignment', 'personalization_score', 'ideological_diversity']] = df.apply(run_simulations_and_stats, axis=1)

    # 5. Overige variabelen
    df['political_exposure'] = df['pol_video_count'] / df['total_videos'].astype(float)
    df['political_interest'] = pd.to_numeric(df['Q13_1'], errors='coerce')

    # 6. Export naar R
    final_cols = [
        'Respondent_ID', 'age', 'Q16', 'total_videos',
        'political_identity_self', 'political_identity_party', 'political_identity_index', 
        'political_interest', 'ideological_median', 'ideological_mean', 'ideological_alignment', 
        'personalization_score', 'ideological_diversity', 'political_exposure', 'usage_intensity'
    ]
    
    df_final = df[final_cols].rename(columns={'Q16': 'gender'}).dropna(subset=['ideological_alignment'])
    df_final.to_csv("master_dataset.csv", index=False)
    
    print(f"Klaar! Dataset bevat {len(df_final)} respondenten en alle benodigde variabelen.")

if __name__ == "__main__":
    calculate_final_variables("master_intermediate.pkl", "tiktok_library.json")