from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Dict, Text, Any, List
from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.events import SlotSet
import regex as re
import csv
import os
import datetime
import requests
import pandas as pd

SHIPMENT_DB = {
    "123456789": {
        "status": "In transit",
        "source": "400807",
        "destination": "400709",
        "time": "1"  
    },
    "987654321": {
        "status": "Delivered",
        "source": "123456",
        "destination": "654321",
        "time": "0"  
    },
    "123454321": {
        "status": "Pending Pickup",
        "source": "400001",
        "destination": "400007", 
        "time": "3" 
    }
}

class ValidateTrackingForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_tracking_form"

    def validate_tracking_id(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        match = re.search(r"\b\d{9}\b", str(slot_value))

        if match:
            tracking_id = match.group()

            # Check if it contains any non-digit characters (invalid)
            if bool(re.search(r"\D", str(slot_value))) and "tracking" not in str(slot_value).lower():
                dispatcher.utter_message(response="utter_invalid_tracking_id")
                return {"tracking_id": None}

            # Check if tracking ID exists in SHIPMENT_DB
            if tracking_id in SHIPMENT_DB:
                return {"tracking_id": tracking_id}
            else:
                dispatcher.utter_message(text=f"Tracking ID {tracking_id} not found. Please check and try again.")
                return {"tracking_id": None}
        else:
            dispatcher.utter_message(response="utter_invalid_tracking_id")
            return {"tracking_id": None}


class ValidateAddressForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_address_form"

    def validate_source_address(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        source_pin = str(slot_value).strip()

        if re.fullmatch(r"\d{6}", source_pin):
            return {"source_address": source_pin}
        else:
            dispatcher.utter_message(text="Please enter a valid 6-digit PIN code for the source address.")
            return {"source_address": None}

    def validate_dest_address(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        dest_pin = str(slot_value).strip()

        if re.fullmatch(r"\d{6}", dest_pin):
            return {"dest_address": dest_pin}
        else:
            dispatcher.utter_message(text="Please enter a valid 6-digit PIN code for the destination address.")
            return {"dest_address": None}

class ActionLookupShipmentStatus(Action):
    def name(self) -> Text:
        return "action_lookup_shipment_status"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[Dict[Text, Any]]:
        tracking_id = tracker.get_slot("tracking_id")

        if not tracking_id:
            dispatcher.utter_message(text="I can't look up a shipment without a tracking ID.")
            return []

        if tracking_id in SHIPMENT_DB:
            info = SHIPMENT_DB[tracking_id]
            dispatcher.utter_message(text=f"Your shipment with ID <b>{tracking_id}</b> is <b>{info['status']}</b>. It is travelling from <b>{info['source']}</b> to <b>{info['destination']}</b>.")

        return [SlotSet("tracking_id", None)]

class ActionEstimateDelivery(Action):
    def name(self) -> Text:
        return "action_estimate_delivery"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[Dict[Text, Any]]:
        tracking_id = tracker.get_slot("tracking_id")

        if not tracking_id:
            dispatcher.utter_message(text="I can't estimate a delivery time without a tracking ID.")
            return []
        
        if tracking_id in SHIPMENT_DB:
            info = SHIPMENT_DB[tracking_id]
            try:
                delivery_time = int(info['time'])
                if delivery_time > 0:
                    dispatcher.utter_message(text=f"Your shipment with ID <b>{tracking_id}</b> is estimated to arrive in <b>{delivery_time} day(s)</b>.")
                else:
                    dispatcher.utter_message(text="This package has <b>already been delivered<b>.")
            except (KeyError, ValueError):
                dispatcher.utter_message(text=f"I couldn't find a delivery estimate for shipment <b>{tracking_id}</b>.")
        return [SlotSet("tracking_id", None)]

class ActionChangeAddress(Action):
    def name(self) -> Text:
        return "action_change_address"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        tracking_id = tracker.get_slot("tracking_id")
        new_source = tracker.get_slot("source_address")
        new_dest = tracker.get_slot("dest_address")

        if not new_source or not new_dest:
            dispatcher.utter_message(text="Please provide both new source and destination addresses.")
            return []

        SHIPMENT_DB[tracking_id]['source'] = new_source
        SHIPMENT_DB[tracking_id]['destination'] = new_dest

        dispatcher.utter_message(
            text=f"The addresses for shipment ID <b>{tracking_id}</b> have been updated:\nSource: <b>{SHIPMENT_DB[tracking_id]['source']}</b>\nDestination: <b>{SHIPMENT_DB[tracking_id]['destination']}</b>"
        )

        return [SlotSet("source_address", None), SlotSet("dest_address", None), SlotSet("tracking_id", None)]

class ActionHandleRating(Action):
    def name(self):
        return "action_handle_star_rating"

    def run(self, dispatcher, tracker, domain):
        stars = tracker.get_slot("rating")
        if stars:
            dispatcher.utter_message(text=f"Thanks for rating us <b>{int(stars)} star{'s' if stars > 1 else ''}!</b>")
        else:
            dispatcher.utter_message(text="Thanks for your feedback.")
        return [SlotSet("rating", None)]

class ActionLogRating(Action):
    def name(self) -> str:
        return "action_log_rating"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:

        # Get the rating and user ID
        rating = tracker.get_slot("rating") or tracker.latest_message['entities'][0]['value']
        sender_id = tracker.sender_id
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # CSV file path
        file_path = "ratings_log.csv"

        # Check if file exists, if not write header
        file_exists = os.path.isfile(file_path)
        with open(file_path, mode="a", newline="") as csv_file:
            fieldnames = ["timestamp", "user_id", "rating","summary","sentiment"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            # Write the rating entry
            writer.writerow({
                "timestamp": timestamp,
                "user_id": sender_id,
                "rating": rating
            })

        return [SlotSet("rating", rating)]



class ActionSummarizeChat(Action):
    def name(self) -> Text:
        return "action_summarize_chat"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        csv_path = os.path.join(os.path.dirname(__file__), "..", "ratings_log.csv")

        csv_path = os.path.abspath(csv_path)
        df = pd.read_csv(csv_path)    
        latest_row = df.iloc[-1]
        rating = latest_row["rating"]
        messages = []
        for event in tracker.events:
            if event.get("event") == "user":
                messages.append(f"User: {event.get('text')}")
            elif event.get("event") == "bot":
                msg = event.get("text")
                if msg:
                    messages.append(f"Bot: {msg}")

        conversation = "\n".join(messages)  

        # Step 2: Prompt for summary + sentiment
        prompt = f"""
Here is a conversation between a user and a chatbot and the user's rating.

Conversation:
{conversation}

User Rating: {rating}

Please respond in this format:

**Summary:** <summary>  
**Sentiment:** <Positive/Neutral/Negative>

Output everything in a single paragraph block.
Avoid extra newlines. Respond as short as possible.
"""
        
        # Step 3: Call Ollama API
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama3.2:latest", "prompt": prompt, "stream": False}
            )
            result = response.json()["response"]
        except Exception as e:
            result = f"Error getting summary from Ollama: {e}"
        result = result.replace('\n', ' ').strip()

        # Step 4: Send to database
        i= result.find("Sentiment")
        summary= result[12:i-2]
        sentiment= result[i+12:]

        with open("ratings_log.csv", mode="r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            fieldnames = ["timestamp", "user_id", "rating", "summary", "sentiment"]

        # Update the last row
        if rows:
            rows[-1]['summary'] = summary
            rows[-1]['sentiment'] = sentiment
        else:
            print("CSV is empty!")

        # Write everything back
        with open("ratings_log.csv", mode="w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return []
