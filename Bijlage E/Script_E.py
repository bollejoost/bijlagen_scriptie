import json
from datetime import datetime
import os
import requests
import time

creator_cache = {}

# functie om creator handle op te halen als nodig voor selective exposure check
def get_creator_via_oembed(url):
    """Haalt de handle van de maker op via de officiële TikTok oEmbed API."""
    if url in creator_cache:
        return creator_cache[url]
    
    try:
        api_url = f"https://www.tiktok.com/oembed?url={url}"
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # 'author_unique_id' is de technische term voor de handle 
            handle = data.get("author_unique_id")
            creator_cache[url] = handle
            return handle
    except Exception as e:
        print(f"Waarschuwing: oEmbed mislukt voor {url}: {e}")
    
    return None

# functie om de TikTokdata te verwerken volgens de stappen beschreven in het plan
def process_tiktok_data(respondent_json_path, library_json_path):
    print(f"--- Start verwerking: {respondent_json_path} ---")
    
    with open(library_json_path, 'r') as f:
        library = json.load(f)
    
    party_scores = {
        "BIJ1": 0.5, "PvdD": 1.2, "SP": 1.8, "GL-PvdA": 2.2, 
        "Volt": 3.8, "DENK": 4.2, "D66": 4.8, "50PLUS": 5.5,
        "NSC": 6.2, "CDA": 6.4, "VVD": 7.8, "BBB": 8.1, 
        "JA21": 8.9, "PVV": 9.3, "FvD": 9.8
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
    following = set(res_data.get("Following", []))
    res_id = res_data.get("Respondent_ID")

    # 3. Stap 1: Identificeer politieke video's uit de bibliotheek
    for video in watch_history:
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

    # 4. Stap 2: Selective Exposure Check (oEmbed voor buren)
    print("Checken op selective exposure (oEmbed)...")
    
    for i in range(len(watch_history)):
        video = watch_history[i]
        
        # We checken alleen creators als de video politiek is EN de maker wordt gevolgd
        if video['is_political'] and video['creator'] in following:
            
            def is_neighbor_followed(idx):
                if idx < 0 or idx >= len(watch_history):
                    return False
                
                neighbor = watch_history[idx]
                # Als creator al bekend is (omdat hij politiek was), gebruik die. 
                # Zo niet, haal hem op via oEmbed.
                handle = neighbor.get('creator')
                if not handle:
                    handle = get_creator_via_oembed(neighbor['short_link'])
                    neighbor['creator'] = handle # Cache in de lijst zelf
                
                return handle in following

            # 3-op-een-rij logica
            f_m2 = is_neighbor_followed(i-2)
            f_m1 = is_neighbor_followed(i-1)
            f_p1 = is_neighbor_followed(i+1)
            f_p2 = is_neighbor_followed(i+2)

            # De reeksen: [m2, m1, i] OF [m1, i, p1] OF [i, p1, p2]
            if (f_m2 and f_m1) or (f_m1 and f_p1) or (f_p1 and f_p2):
                video['selective_exposure'] = True
            else:
                video['selective_exposure'] = False
        else:
            video['selective_exposure'] = False

    # 5. Gebruiksintensiteit
    dates = [datetime.strptime(v['date'], '%Y-%m-%d %H:%M:%S') for v in watch_history]
    days_diff = (max(dates) - min(dates)).days + 1
    usage_intensity = len(watch_history) / days_diff

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

    # Opslaan
    output_name = f"processed_{res_id}.json"
    with open(output_name, 'w') as f:
        json.dump(final_output, f, indent=4)
    
    print(f"Resultaat staat in {output_name}")

if __name__ == "__main__":
    # Verander hier de bestandsnaam voor de respondent:
    INPUT = "respondentfile.json"
    LIB = "tiktok_library.json"
    
    process_tiktok_data(INPUT, LIB)