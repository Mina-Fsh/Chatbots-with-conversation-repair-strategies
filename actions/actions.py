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


class ActionProduct_description(Action):
    '''custom action for product_description intent
       reads descriptions based on the card type'''

    def name(self) -> Text:
        return "action_product_description"
		
    def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            requestedProductName = tracker.get_slot("product_name")
            log.info("requested product name is: {}".format(requestedProductName))
            
            # Validates the location name if it exists
            if requestedProductName == 'credit card':
                dispatcher.utter_message("A {} is a card that ...".format(requestedProductName))
                return [SlotSet("card_name", requestedProductName)]   
            elif requestedProductName == 'Master card':
                dispatcher.utter_message("A {} is a card that ...".format(requestedProductName))
                return [SlotSet("card_name", requestedProductName)]
            elif requestedProductName == 'Visa card':
                dispatcher.utter_message("A {} is a card that ...".format(requestedProductName))
                return [SlotSet("card_name", requestedProductName)]
            elif requestedProductName == 'bank account':
                dispatcher.utter_message("A {} is a free account that ...".format(requestedProductName))
                return [SlotSet("card_name", requestedProductName)]
            else:
                # Telling the user that the card name is not known
                dispatcher.utter_message("I don't know about this card. You can ask me questions about Credit card, Master card or Visa card!")
                return [SlotSet("card_name", None)]


class ActionProduct_application(Action):
    '''custom action for product_application intent
       reads descriptions based on the card type'''

    def name(self) -> Text:
        return "action_product_application"
		
    def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            requestedProductName = tracker.get_slot("card_name")
            log.info("requested card name is: {}".format(requestedProductName))
            
            # Validates the location name if it exists
            if requestedProductName == 'credit card':
                dispatcher.utter_message("A {} is a card that ...".format(requestedProductName))
                return [SlotSet("card_name", requestedProductName)]   
            elif requestedProductName == 'Master card':
                dispatcher.utter_message("A {} is a card that ...".format(requestedProductName))
                return [SlotSet("card_name", requestedProductName)]
            elif requestedProductName == 'Visa card':
                dispatcher.utter_message("A {} is a card that ...".format(requestedProductName))
                return [SlotSet("card_name", requestedProductName)]
            elif requestedProductName == 'bank account':
                dispatcher.utter_message("A {} is a free account that ...".format(requestedProductName))
                return [SlotSet("card_name", requestedProductName)]
            else:
                # Telling the user that the card name is not known
                dispatcher.utter_message("I don't know about this card. You can ask me questions about Credit card, Master card or Visa card!")
                return [SlotSet("card_name", None)]

