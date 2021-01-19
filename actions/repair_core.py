import logging
from typing import Any, Dict, List, Text
from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import (
    FollowupAction,
    UserUtteranceReverted,
    EventType,
)

INTENT_DESCRIPTION_MAPPING_PATH = "actions/intent_description_mapping.csv"

logger = logging.getLogger(__name__)


class ActionDefaultFallback(Action):
    """Executes the fallback action and goes back to the previous state
    of the dialogue"""
    def name(self) -> Text:
        return "action_default_fallback"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:

        repair_strategy = tracker.get_slot("repair_strategy_name")

        # Fallback caused by TwoStageFallbackPolicy
        if (
            len(tracker.events) >= 12
            and tracker.events[-12].get("name") == "action_system_repair"
        ):

            dispatcher.utter_message(template="utter_restart_with_button")

            return []

        # Fallback caused by Core
        else:
            if repair_strategy == "system_repair":
                message_title = "Hmm... I'm afraid I didn't get what you just said."
            else:
                conversation_turns = self.count_turns(tracker)
                logger.info(f"conv turns is: {conversation_turns}")
                if conversation_turns > 20:
                    fatigue_warning = "\n- Our conversation has gotten too long, which means I have saved many keywords from our conversation history in my memory; this could mislead me."
                else:
                    fatigue_warning = ""

                confusion_warning = (
                        "\n- In this conversation, we have taken off an expected conversation flow."
                    )
                message = "Hmm... I'm afraid I didn't get what you just said. I think this information can help you:"

                message_title = message + confusion_warning + fatigue_warning

            dispatcher.utter_message(text=message_title)
            return [UserUtteranceReverted()]

    def count_turns(
        self,
        tracker: Tracker
    ) -> int:

        conv_turns = 0
        user_event_list = []
        for events in tracker.events_after_latest_restart():
            if events["event"] == "user":
                user_event_list.append(events)
                conv_turns += 1

        return conv_turns