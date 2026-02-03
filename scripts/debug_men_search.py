import requests
import json

# Configuration
URL = "http://localhost:8000/api/ai-query/"
USER_ID = 5 

def test_men_search(prompt, user_gender='men'):
    # Note: This script assumes the server is running
    # To truly simulate, we should ensure a user with gender='men' actually exists in DB
    # For now, let's just use an existing user id and assume we can force their context if needed
    
    data = {
        "prompt": prompt,
        "user_id": USER_ID
    }
    
    try:
        response = requests.post(URL, json=data)
        print(f"\n--- Testing prompt: '{prompt}' for user gender: '{user_gender}' ---")
        if response.status_code == 200:
            res = response.json()
            print(f"AI Message: {res['message']}")
            print(f"Products Count: {len(res['products'])}")
            print(f"Extracted Intent: {res['machine_readable_json']}")
            if len(res['products']) > 0:
                print(f"First product gender: {res['products'][0]['gender']}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_men_search("show me some products")
    test_men_search("men shirts")
    test_men_search("blue shirts for men")
