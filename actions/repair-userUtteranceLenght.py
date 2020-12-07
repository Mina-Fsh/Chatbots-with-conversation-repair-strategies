import logging
from typing import Any, Dict, List, Text
from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import (
    EventType,
    FollowupAction,
)

INTENT_DESCRIPTION_MAPPING_PATH = "actions/intent_description_mapping.csv"

logger = logging.getLogger(__name__)


class ActionRepairLabelUserUtteranceLenght(Action):
    """Responses to the user text based on the utterance's length.!"""

    def name(self) -> Text:
        return "action_repair_label_user_utterance_length"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:

        user_msg = tracker.latest_message['text']
        user_msg_len = len(user_msg.split())
        logger.info(f"{user_msg}, {user_msg_len}")

        if user_msg_len < 3:
            message_title = "You expressed yourself very briefly, unfortunately I couldn't get you. 😕"
        elif user_msg_len < 10 and  user_msg_len > 3:
            message_title = "Eventhough you elaborated your request nicely, I still couldn't get you. I'm sorry. 🤐"
        else:
            message_title = "You gave me such long information and it is confusing me! 😵"

        dispatcher.utter_message(text=message_title)
        return [FollowupAction("action_listen")]
