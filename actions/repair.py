import logging
from typing import Any, Dict, List, Text
from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import (
    FollowupAction
)

INTENT_DESCRIPTION_MAPPING_PATH = "actions/intent_description_mapping.csv"

logger = logging.getLogger(__name__)


class ActionConfigureRepairStrategy(Action):

    def name(self) -> Text:
        return "action_configure_repair_strategy"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        message_title = "Which repair strategy would you like to have in this \
         conversation in case of a breakdown?"

        buttons = [
            {
                "title": "Give me directions to proceed.",
                "payload": "system_repair",
            },
            {
                "title": "Explain me possible reasons behind the breakdown.",
                "payload": "self_assisted_repair",
            },
            {
                "title": "Give me directions to proceed, or if relevant \
                    explain me possible reasons behind the breakdown..",
                "payload": "mix_repair",
            }  
        ]

        dispatcher.utter_message(text=message_title, buttons=buttons)

        return []


class ActionRepair(Action):

    def name(self) -> Text:
        return "action_repair"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        logger.info(f"length: { len(tracker.events) }")

        # Checks a list consisting of the last four elements => starting from
        # element -15 to the end of the list ":"
        # https://stackoverflow.com/questions/9542738/python-find-in-list

        logger.info(f'clause: {next((True for event in tracker.events[-15:] if event.get("name") == "system_repair"), False) }')

        repair_strategy = tracker.get_slot("repair_strategy_name")

        # Fallback caused by TwoStageFallbackPolicy
        if (
            len(tracker.events) >= 15 and
            next((True for event in tracker.events[-15:] if event.get("name") == "action_repair" and repair_strategy == "system_repair"), False)
        ):

            dispatcher.utter_message(template="utter_restart_with_button")

            return []
        #######

        if repair_strategy == "system_repair":
            return [FollowupAction("action_system_repair")]
        elif repair_strategy == "self_assisted_repair":
            return [FollowupAction("action_self_assisted_repair")]
        elif repair_strategy == "mix_repair":
            return [FollowupAction("action_self_assisted_repair")]
        else:
            dispatcher.utter_message("I do not know this repair strategy")
        return []
