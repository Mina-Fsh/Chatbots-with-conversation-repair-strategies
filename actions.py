from typing import Dict, Text, Any, List
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, FollowupAction

import logging
log = logging.getLogger("my-logger")

class ActionRepeat(Action):
    '''custom action repeating the last bot utterance'''

    def name(self) -> Text:
        return "action_repeat"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            user_ignore_count = 2
            count = 0
            tracker_list = []

            while user_ignore_count > 0:
                event = tracker.events[count].get('event')
                if event == 'user':
                    user_ignore_count = user_ignore_count - 1
                if event == 'bot':
                    tracker_list.append(tracker.events[count])
                count = count - 1

            i = len(tracker_list) - 1
            while i >= 0:
                data = tracker_list[i].get('data')
                if data:
                    if "buttons" in data:
                        dispatcher.utter_message(text=tracker_list[i].get('text'), buttons=data["buttons"])
                    else:
                        dispatcher.utter_message(text=tracker_list[i].get('text'))
                i -= 1

            return []


class ActionCard_descriptions(Action):
    '''custom action for card_descriptions intent
       reads descriptions based on the card type'''

    def name(self) -> Text:
        return "action_card_descriptions"
		
    def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            requestedCardName = tracker.get_slot("card_name")
            log.info("requested card name is: {}".format(requestedCardName))
            
            # Validates the location name if it exists
            if requestedCardName == 'Credit card':
                dispatcher.utter_message("A {} is a card that ...".format(requestedCardName))
                return [SlotSet("card_name", requestedCardName)]   
            elif requestedCardName == 'Master card':
                dispatcher.utter_message("A {} is a card that ...".format(requestedCardName))
                return [SlotSet("card_name", requestedCardName)]
            elif requestedCardName == 'Visa card':
                dispatcher.utter_message("A {} is a card that ...".format(requestedCardName))
                return [SlotSet("card_name", requestedCardName)]
            else:
                # Telling the user that the card name is not known
                dispatcher.utter_message("I don't know about this card. You can ask me questions about Credit card, Master card or Visa card!")
                return [SlotSet("card_name", None)]


