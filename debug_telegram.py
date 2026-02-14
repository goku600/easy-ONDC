from dotenv import load_dotenv
load_dotenv()

from src.services.telegram_service import TelegramService
import time

def debug_intent():
    service = TelegramService()
    
    test_messages = [
        "Register my grocery store in Bangalore",
        "Find plumbers nearby",
        "Hi",
        "I need a laptop repair shop",
        "My shop sells organic vegetables"
    ]
    
    print("--- Starting Debug ---")
    for msg in test_messages:
        print(f"\nScanning: '{msg}'")
        try:
            intent = service.classify_intent(msg)
            print(f"Result: '{intent}'")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(1)

if __name__ == "__main__":
    debug_intent()
