import requests

def main():
    location = input("Enter a location to get the weather: ")
    payload = {
        "tool": "get_weather",
        "args": {
            "location": location
        }
    }
    response = requests.post("http://localhost:8000/mcp/invoke", json=payload)
    if response.status_code == 200:
        print("Weather Info:", response.json()["result"])
    else:
        print("Error:", response.text)

if __name__ == "__main__":
    main()