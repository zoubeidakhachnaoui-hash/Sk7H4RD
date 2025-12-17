
import requests
from bs4 import BeautifulSoup
import json
import time

def scrape_emotes():
    """Scrape all emotes from ff-item.netlify.app"""
    all_emotes = []
    base_url = "https://ff-item.netlify.app/"
    
    # Scrape from all pages
    pages = ['?t=emote', '?p=2&t=emote', '?p=3&t=emote', '?p=4&t=emote', '?p=5&t=emote', '?p=6&t=emote']
    
    for page in pages:
        try:
            print(f"Scraping {base_url}{page}...")
            response = requests.get(base_url + page, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all emote items
            emote_items = soup.find_all('div', class_='item')
            
            for item in emote_items:
                try:
                    # Extract image URL
                    img = item.find('img')
                    img_url = img.get('src') if img else None
                    
                    # Extract emote name
                    name_elem = item.find('div', class_='name')
                    name = name_elem.text.strip() if name_elem else 'Unknown'
                    
                    # Extract emote ID from image URL or data attributes
                    emote_id = None
                    if img_url:
                        # Try to extract ID from URL
                        parts = img_url.split('/')
                        for part in parts:
                            if part.isdigit() and len(part) >= 9:
                                emote_id = part.replace('.png', '').replace('.jpg', '')
                                break
                    
                    if emote_id and name:
                        image_url = img_url if img_url and img_url.startswith('http') else (base_url + img_url if img_url else '')
                        emote_data = {
                            'id': emote_id,
                            'name': name,
                            'image': image_url
                        }
                        
                        # Avoid duplicates
                        if not any(e['id'] == emote_id for e in all_emotes):
                            all_emotes.append(emote_data)
                            print(f"  Found: {emote_id} - {name}")
                            
                except Exception as e:
                    print(f"  Error parsing item: {e}")
                    continue
            
            time.sleep(1)  # Be respectful to the server
            
        except Exception as e:
            print(f"Error scraping page {page}: {e}")
            continue
    
    # Save to JSON file
    with open('emotes_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_emotes, indent=2, fp=f, ensure_ascii=False)
    
    print(f"\n✅ Total emotes scraped: {len(all_emotes)}")
    print(f"✅ Data saved to emotes_data.json")
    
    return all_emotes

if __name__ == '__main__':
    emotes = scrape_emotes()
