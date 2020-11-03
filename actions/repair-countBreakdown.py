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


class ActionRepairCountBreakdown(Action):
    """Shows options in the first 5 sessions and after that asks for rephrase!"""

    def name(self) -> Text:
        return "action_repair_count_breakdwon"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:

        breakdown_counter = 0
        action_counter = 0
        for events in tracker.events:
            if events["event"] == "action" and events["name"] == "action_repair": 
                breakdown_counter +=1
            if events["event"] == "action" and events["name"] != "action_listen": 
                action_counter +=1
        logger.debug(f"You already had {breakdown_counter} breakdowns in this conversation!")

        if breakdown_counter <= 5:
            return [FollowupAction("action_repair_options")]
        elif breakdown_counter > 5:
            dispatcher.utter_message(template = "utter_capabilities_repair")
        return[]
    
