import logging
import json
import requests
import random
from datetime import datetime
from typing import Any, Dict, List, Text, Union, Optional
from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction, REQUESTED_SLOT
from rasa_sdk.events import (
    SlotSet,
    EventType,
    ActionExecuted,
    SessionStarted,
    Restarted,
    UserUtteranceReverted,
    ConversationPaused,
    FollowupAction,
)

from actions.parsing import (
    parse_duckling_time_as_interval,
    parse_duckling_time,
    get_entity_details,
    parse_duckling_currency,
)

from actions.profile import create_mock_profile
from actions import config
from dateutil import parser

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
