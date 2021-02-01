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

        action_event_list = []
        for events in tracker.events_after_latest_restart():
            if events["event"] == "action":
                action_event_list.append(events)
        action_event_list_clean = [i for i in action_event_list if not (i['name'] == 'action_listen')]
        logger.info(f"Cleaned action events are: {action_event_list_clean}")
        # {'event': 'action', 'timestamp': 1612187448.9603305, 'name': 'utter_rephrase', 'policy': 'policy_2_RulePolicy', 'confidence': 1.0, 'action_text': None}, 

        repair_strategy = tracker.get_slot("repair_strategy_name")

        if repair_strategy == "system_repair":
            # Fallback caused by TwoStageFallbackPolicy
            last_action_needed_for_two_stage = ["action_system_repair", "utter_rephrase"]
            if (
                len(action_event_list) >= 2
                and action_event_list_clean[-1].get("name") in last_action_needed_for_two_stage
            ):
                dispatcher.utter_message(template="utter_restart_with_button")
                return []
            else:
                return [FollowupAction("action_system_repair")]
        elif repair_strategy == "mix_repair":
            # Fallback caused by TwoStageFallbackPolicy
            last_action_needed_for_two_stage = ["action_mix_repair", "utter_rephrase"]
            if (
                len(action_event_list) >= 2
                and action_event_list_clean[-1].get("name") in last_action_needed_for_two_stage
            ):
                dispatcher.utter_message(template="utter_restart_with_button")
                return []
            else:
                return [FollowupAction("action_mix_repair")]
        elif repair_strategy == "self_assisted_repair":
            return [FollowupAction("action_self_assisted_repair")]
        else:
            return [FollowupAction("action_system_repair")]
        return []
