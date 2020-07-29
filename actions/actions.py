from typing import Dict, Text, Any, List, Union
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, FollowupAction
from rasa_sdk.forms import FormAction
import logging

log = logging.getLogger("Debugging")

##############################################
# Classes for the gear assembly Bot functionality.
##############################################
class OrderGearboxForm(FormAction):
    """Example of a custom form action"""

    def name(self):
        """Unique identifier of the form"""

        return "order_gearbox_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""
        
        return ["num_gears", "gear_one_size", "gear_one_polishing", "gear_two_size", "gear_two_polishing", "gear_three_size", "gear_three_polishing"]


    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""
        
        return {
            "num_gears": [
            self.from_entity(entity="num_gears", intent=["inform", "order_gearbox"]),
            self.from_intent(intent="deny", value="None"),
            ],
            "gear_one_size": [
                self.from_entity(entity="gear_one_size", intent=["inform", "order_gearbox"]),
                self.from_intent(intent="deny", value="None"),
            ],
            "gear_two_size": [
                self.from_entity(entity="gear_two_size", intent=["inform", "order_gearbox"]),
                self.from_intent(intent="deny", value="None"),
            ],
            "gear_three_size": [
                self.from_entity(entity="gear_three_size", intent=["inform", "order_gearbox"]),
                self.from_intent(intent="deny", value="None"),
            ],
            "gear_one_polishing": [
                self.from_entity(entity="gear_one_polishing", intent=["inform", "order_gearbox"]),
                self.from_intent(intent="affirm", value=True),
                self.from_intent(intent="deny", value=False),
            ],
            "gear_two_polishing": [
                self.from_entity(entity="gear_two_polishing", intent=["inform", "order_gearbox"]),
                self.from_intent(intent="affirm", value=True),
                self.from_intent(intent="deny", value=False),
            ],
            "gear_three_polishing": [
                self.from_entity(entity="pgear_three_polishing", intent=["inform", "order_gearbox"]),
                self.from_intent(intent="affirm", value=True),
                self.from_intent(intent="deny", value=False),
            ]
        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        # utter submit template
        dispatcher.utter_message(template="utter_submit")
        return []