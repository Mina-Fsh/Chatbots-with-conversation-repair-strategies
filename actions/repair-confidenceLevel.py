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


class ActionRepairLabelConfidency(Action):
    """Responses to the user text based on it's confidency."""

    def name(self) -> Text:
        return "action_repair_label_confidenc_level"
    
    def __init__(self) -> None:
        import pandas as pd

        self.intent_mappings = pd.read_csv(INTENT_DESCRIPTION_MAPPING_PATH)
        self.intent_mappings.fillna("", inplace=True)
        self.intent_mappings.entities = self.intent_mappings.entities.map(
            lambda entities: {e.strip() for e in entities.split(",")}
        )

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:

        intent_ranking = tracker.latest_message.get("intent_ranking", [])
        if len(intent_ranking) > 1:
            highest_ranked_intent_confidence = intent_ranking[0].get("confidence")
            highest_ranked_intent_name = intent_ranking[0].get("name")
            if highest_ranked_intent_confidence >= 0.75:
                message_title = "😊 I'm Highly confident that this is what you mean:"
            elif highest_ranked_intent_confidence < 0.75 and  highest_ranked_intent_confidence >= 0.6:
                message_title = "🙂 I'm somehow familiar with this topic, I think you mean this:"
            elif highest_ranked_intent_confidence < 0.6 and  highest_ranked_intent_confidence >= 0.4:
                message_title = "😕 I have serious doubts about what you are saying... this is the only thing that comes to my mind:"
            elif highest_ranked_intent_confidence < 0.4 and  highest_ranked_intent_confidence >= 0.1:
                message_title = "😵 I'm really confused, but there is a small chance you mean this:"
            else:
                message_title = "🤥 I have no idea what you mean, here is my unlucky guess:"
        
        entities = tracker.latest_message.get("entities", [])
        entities = {e["entity"]: e["value"] for e in entities}

        entities_json = json.dumps(entities)

        buttons = []
        
        button_title = self.get_button_title(highest_ranked_intent_name, entities)
            
        buttons.append(
            {
                "title": button_title,
                "payload": f"/{highest_ranked_intent_name}{entities_json}",
            }
        )

        dispatcher.utter_message(text=message_title, buttons=buttons)
        return [FollowupAction("action_listen")]
    
    def get_button_title(
        self, intent: Text, entities: Dict[Text, Text]
    ) -> Text:
        default_utterance_query = self.intent_mappings.intent == intent
        utterance_query = (
            self.intent_mappings.entities == entities.keys()
        ) & (default_utterance_query)

        utterances = self.intent_mappings[utterance_query].button.tolist()

        if len(utterances) > 0:
            button_title = utterances[0]
        else:
            utterances = self.intent_mappings[
                default_utterance_query
            ].button.tolist()
            button_title = utterances[0] if len(utterances) > 0 else intent

        return button_title.format(**entities)
