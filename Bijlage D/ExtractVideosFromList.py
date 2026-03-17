#################################################################################
#   Dit script is gebruikt om de video-id's van alle politieke TikTokaccounts   #
#   te scrapen en in tiktok_library.json te plaatsen                            #
#################################################################################

import yt_dlp
import json
import time
import random
import os

LIBRARY_FILE = "tiktok_library.json"

def load_library():
    """Loads the existing library if the file exists, otherwise returns an empty dictionary."""
    if os.path.exists(LIBRARY_FILE):
        try:
            with open(LIBRARY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: {LIBRARY_FILE} is corrupted. Starting fresh.")
    return {}

def save_library(library_data):
    """Saves the current state of the library to the JSON file."""
    with open(LIBRARY_FILE, 'w', encoding='utf-8') as f:
        json.dump(library_data, f, indent=4)

def get_video_ids(account_url):
    """Uses yt-dlp to scrape just the video IDs from a profile."""
    
    ydl_opts = {
        'extract_flat': True,  
        'quiet': True,         
        'sleep_requests': 1.5, # Wait 1.5s between scrolling
        
        # adding personal cookies for login
        'cookiesfrombrowser': ('chrome',), 
    }

    video_ids = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(account_url, download=False)
        if 'entries' in info:
            for video in info['entries']:
                vid = video.get('id')
                if vid:
                    video_ids.append(vid)
    return video_ids

def build_library(accounts_list):
    library = load_library()
    total_accounts = len(accounts_list)
    
    print(f"Starting library build. Loaded {len(library)} parties from existing database.\n")

    for index, account in enumerate(accounts_list, 1):
        party = account['party']
        url = account['url']
        
        # Extract the username 
        username = url.rstrip('/').split('@')[-1]
        
        # Ensure the party exists in our dictionary
        if party not in library:
            library[party] = {}
            
        # Check if already scraped 
        if username in library[party]:
            print(f"[{index}/{total_accounts}] ✅ Skipping {party} / @{username} (Already in library)")
            continue
            
        print(f"[{index}/{total_accounts}] 🔍 Scraping {party} / @{username}...")
        
        try:
            # Scrape the IDs
            vids = get_video_ids(url)
            
            # Save them to the library structure
            library[party][username] = vids
            print(f"    -> Successfully found {len(vids)} videos.")
            
            # Immediately save to disk 
            save_library(library)
            
            # If this is not the last account, sleep to avoid rate limits
            if index < total_accounts:
                sleep_time = random.uniform(5.0, 15.0)
                print(f"    -> Sleeping for {sleep_time:.1f} seconds to prevent rate limiting...\n")
                time.sleep(sleep_time)
                
        except Exception as e:
            print(f"\n❌ ERROR scraping @{username}: {e}")
            print("TikTok has likely temporarily blocked your connection (HTTP Error 429 or 403).")
            print("The script has saved all progress up to this point.")
            break # Stop the loop 

    print("\nRun complete! Data saved to", LIBRARY_FILE)

if __name__ == "__main__":
    # --- DE VOLLEDIGE LIJST ---
    full_accounts_list = [
        # CDA
        {"party": "CDA", "url": "https://www.tiktok.com/@cdavandaag"},
        {"party": "CDA", "url": "https://www.tiktok.com/@henri.bontenbal"},
        {"party": "CDA", "url": "https://www.tiktok.com/@teamhenri2025"},
        {"party": "CDA", "url": "https://www.tiktok.com/@hannekesteenklok"},
        {"party": "CDA", "url": "https://www.tiktok.com/@derkboswijk"},
        {"party": "CDA", "url": "https://www.tiktok.com/@cdjaonline"},

        # D66
        {"party": "D66", "url": "https://www.tiktok.com/@robjettend66"},
        {"party": "D66", "url": "https://www.tiktok.com/@democraten66"},
        {"party": "D66", "url": "https://www.tiktok.com/@d66wijchen"},
        {"party": "D66", "url": "https://www.tiktok.com/@d66rotterdam"},
        {"party": "D66", "url": "https://www.tiktok.com/@d66woensdrecht"},
        {"party": "D66", "url": "https://www.tiktok.com/@democraten66.almere"},
        {"party": "D66", "url": "https://www.tiktok.com/@d66zoetje"},
        {"party": "D66", "url": "https://www.tiktok.com/@fractied66zeewolde"},
        {"party": "D66", "url": "https://www.tiktok.com/@jdleidenhaaglanden"},
        {"party": "D66", "url": "https://www.tiktok.com/@jongedemocratenamsterdam"},
        {"party": "D66", "url": "https://www.tiktok.com/@d66leiden"},
        {"party": "D66", "url": "https://www.tiktok.com/@d66hrlm"},
        {"party": "D66", "url": "https://www.tiktok.com/@d66purmerend"},
        {"party": "D66", "url": "https://www.tiktok.com/@d66_delft"},
        {"party": "D66", "url": "https://www.tiktok.com/@jonge.democraten"},
        {"party": "D66", "url": "https://www.tiktok.com/@d66.tilburg"},
        {"party": "D66", "url": "https://www.tiktok.com/@jongedemocratenbrabant"},
        {"party": "D66", "url": "https://www.tiktok.com/@d66breda076"},

        # GL/PvdA
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinkspvda"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@jesse.klaver"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@f_timmermans"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinks_pvda010"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinkspvdaalmere"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinkspvda.hlmr"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinkspvdaflevoland"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinkspvdazutphen"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinkspvdalingewaard"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinkspvdadronten"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinkspvdazaanstad"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@gl_pvda_teylingen"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinkspvdazoetermeer"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@glpvda072"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinks.pvda.e"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@glpvdalelystad"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinkspvda.heemskerk"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinkspvdahelmond"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinkspvda.eemnes"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinks_pvda_a"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@glpvda.delft"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinkspvda.nl"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinkspvda.raalte"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinkspvda.rijswijk"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@gl.pvda_kampen"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinks_pvda_hogeland"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@pvda.de.bilt"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinkspvda.westland"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@glpvda.amstelveen"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinkspvda.oss"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinkspvdadenbosch"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@veenendaal.gl.pvda"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@glpvda.voorschoten"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinks_pvda_dalfsen"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@glpvdadruten"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinkspvda.purmerend"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@glpvdaijsselstein"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinkspvdaberkelland"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinkspvda.denhaag"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinkspvda.veldhoven"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@pvdagroenlinks_hulst"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@glpvda_leiden"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinkspvda_aalsmeer"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@glpvdahoorn"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinks.pvda.laarbeek"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@glpvdautrecht"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@roosendaal.gl.pvda"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@glpvdabeekdaelen"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@glpvda.oosterhout"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinkspvda.arnhem"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@glpvda_enschede"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@groenlinkspvdagoo"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@glpvda.tilburg"},
        {"party": "GL-PvdA", "url": "https://www.tiktok.com/@dwarsjs"},

        # VVD
        {"party": "VVD", "url": "https://www.tiktok.com/@kies.vvd"},
        {"party": "VVD", "url": "https://www.tiktok.com/@dilanyesilgoz"},
        {"party": "VVD", "url": "https://www.tiktok.com/@vvd_haarlemmermeer"},
        {"party": "VVD", "url": "https://www.tiktok.com/@vvdamsterdam"},
        {"party": "VVD", "url": "https://www.tiktok.com/@vvd.rotterdam"},
        {"party": "VVD", "url": "https://www.tiktok.com/@vvd.utrecht"},
        {"party": "VVD", "url": "https://www.tiktok.com/@vvdalmere"},
        {"party": "VVD", "url": "https://www.tiktok.com/@tilburgsevvd"},
        {"party": "VVD", "url": "https://www.tiktok.com/@vvdbreda"},
        {"party": "VVD", "url": "https://www.tiktok.com/@jovdonline"},

        # PvdD
        {"party": "PvdD", "url": "https://www.tiktok.com/@partijvoordedieren"},
        {"party": "PvdD", "url": "https://www.tiktok.com/@ines.kosti"},

        # SP
        {"party": "SP", "url": "https://www.tiktok.com/@socialistischepartij"},
        {"party": "SP", "url": "https://www.tiktok.com/@jimmydijk1985"},
        {"party": "SP", "url": "https://www.tiktok.com/@sp.den.bosch"},
        {"party": "SP", "url": "https://www.tiktok.com/@sp_jongeren"},
        {"party": "SP", "url": "https://www.tiktok.com/@sandrabeckerman"},
        {"party": "SP", "url": "https://www.tiktok.com/@spjongerenrotterdam"},

        # ChristenUnie
        {"party": "CU", "url": "https://www.tiktok.com/@mirjam.bikker"},
        {"party": "CU", "url": "https://www.tiktok.com/@christenunie.rotterdam"},
        {"party": "CU", "url": "https://www.tiktok.com/@christenunieutrecht"},
        {"party": "CU", "url": "https://www.tiktok.com/@cuharderwijk.official"},
        {"party": "CU", "url": "https://www.tiktok.com/@christenunieurk"},
        {"party": "CU", "url": "https://www.tiktok.com/@culeiden"},
        {"party": "CU", "url": "https://www.tiktok.com/@renswouwse.cu"},

        # FvD
        {"party": "FvD", "url": "https://www.tiktok.com/@forumvdemocratie"},
        {"party": "FvD", "url": "https://www.tiktok.com/@gideon_van_meijeren"},
        {"party": "FvD", "url": "https://www.tiktok.com/@lidewij.devos"},
        {"party": "FvD", "url": "https://www.tiktok.com/@thierry_baudet"},
        {"party": "FvD", "url": "https://www.tiktok.com/@pepijnfvd"},
        {"party": "FvD", "url": "https://www.tiktok.com/@realfrederikjansen"},
        {"party": "FvD", "url": "https://www.tiktok.com/@jongerenfvd"},
        {"party": "FvD", "url": "https://www.tiktok.com/@tomrusscher"},

        # 50PLUS
        {"party": "50PLUS", "url": "https://www.tiktok.com/@50pluspartij"},

        # JA21
        {"party": "JA21", "url": "https://www.tiktok.com/@juisteantwoord"},
        {"party": "JA21", "url": "https://www.tiktok.com/@ranjith.clemminck"},
        {"party": "JA21", "url": "https://www.tiktok.com/@ja21amsterdam"},
        {"party": "JA21", "url": "https://www.tiktok.com/@ja21noordholland"},
        {"party": "JA21", "url": "https://www.tiktok.com/@ja21zuidholland"},
        {"party": "JA21", "url": "https://www.tiktok.com/@ja21zeeland"},
        {"party": "JA21", "url": "https://www.tiktok.com/@jong.ja21"},

        # DENK
        {"party": "DENK", "url": "https://www.tiktok.com/@denk_nl"},
        {"party": "DENK", "url": "https://www.tiktok.com/@denkjong"},
        {"party": "DENK", "url": "https://www.tiktok.com/@denkdenhaag"},
        {"party": "DENK", "url": "https://www.tiktok.com/@denk.arnhem"},
        {"party": "DENK", "url": "https://www.tiktok.com/@denk.enschede"},
        {"party": "DENK", "url": "https://www.tiktok.com/@denkamsterdam"},
        {"party": "DENK", "url": "https://www.tiktok.com/@da.ergin"},
        {"party": "DENK", "url": "https://www.tiktok.com/@stephanvanbaarle"},

        # BBB
        {"party": "BBB", "url": "https://www.tiktok.com/@bbboptiktok"},

        # Volt
        {"party": "Volt", "url": "https://www.tiktok.com/@volt.nederland"},
        {"party": "Volt", "url": "https://www.tiktok.com/@laurens.dassen"},
        {"party": "Volt", "url": "https://www.tiktok.com/@volt.amsterdam"},

        # BIJ1
        {"party": "BIJ1", "url": "https://www.tiktok.com/@politiek_bij1"},
        {"party": "BIJ1", "url": "https://www.tiktok.com/@amsterdambij1"},
        {"party": "BIJ1", "url": "https://www.tiktok.com/@utrecht.bij1"},
        {"party": "BIJ1", "url": "https://www.tiktok.com/@rotterdambij1"},
        {"party": "BIJ1", "url": "https://www.tiktok.com/@almerebij1"},
        {"party": "BIJ1", "url": "https://www.tiktok.com/@tilburgbij1"},
        {"party": "BIJ1", "url": "https://www.tiktok.com/@delftbij1"},

        # PVV (Unofficial)
        {"party": "PVV (Unofficial)", "url": "https://www.tiktok.com/@pvv_clips"},
        {"party": "PVV (Unofficial)", "url": "https://www.tiktok.com/@pvvfanpagina"},
        {"party": "PVV (Unofficial)", "url": "https://www.tiktok.com/@geertwildersnieuws"},

        # NSC
        {"party": "NSC", "url": "https://www.tiktok.com/@nieuwsociaalcontract"},
    ]
    
    build_library(full_accounts_list)