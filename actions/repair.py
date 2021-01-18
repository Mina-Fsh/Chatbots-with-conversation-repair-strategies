import logging
from typing import Any, Dict, List, Text
from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import (
    FollowupAction,
)

INTENT_DESCRIPTION_MAPPING_PATH = "actions/intent_description_mapping.csv"

logger = logging.getLogger(__name__)


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

        events = tracker.events[-15:]
        logger.info(f"Events are: {events}")
        logger.info(f'clause: {next((True for event in tracker.events[-12:] if event.get("name") == "action_system_repair"), False) }')

        repair_strategy = tracker.get_slot("repair_strategy_name")

        # Fallback caused by TwoStageFallbackPolicy
        if (
            len(tracker.events) >= 4
            and next((True for event in tracker.events[-12:] if event.get("name") == "action_system_repair"), False)
        ):

            dispatcher.utter_message(template="utter_restart_with_button")

            return []
        #######

        if repair_strategy == "system_repair":
            return [FollowupAction("action_system_repair")]
        elif repair_strategy == "self_assisted_repair":
            return [FollowupAction("action_self_assisted_repair")]
        elif repair_strategy == "mix_repair":
            return [FollowupAction("action_mix_repair")]
        else:
            dispatcher.utter_message("I do not know this repair strategy")
        return []
