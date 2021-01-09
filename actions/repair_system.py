import logging
import json
from typing import Any, Dict, List, Text
from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import (
    EventType,
    FollowupAction,
)

INTENT_DESCRIPTION_MAPPING_PATH = "actions/intent_description_mapping.csv"

logger = logging.getLogger(__name__)


class ActionSystemRepair(Action):
    """This action gives options with highest ranked intents
    + asks for rephrase + offer restart."""

    def name(self) -> Text:
        return "action_system_repair"

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
        logger.info(f"Intent ranking is: {intent_ranking}")
        if len(intent_ranking) > 2:
            diff_intent_confidence = intent_ranking[1].get(
                "confidence"
            ) - intent_ranking[2].get("confidence")
            if diff_intent_confidence < 0.2:
                intent_ranking = intent_ranking[1:3]
            else:
                intent_ranking = intent_ranking[1:2]

        first_intent_names = [
            intent.get("name", "")
            for intent in intent_ranking
        ]

        message_title = (
            "Sorry, I'm not sure I've understood "
            "you correctly 🤔 Do you mean..."
        )

        entities = tracker.latest_message.get("entities", [])
        entities = {e["entity"]: e["value"] for e in entities}

        entities_json = json.dumps(entities)

        buttons = []
        for intent in first_intent_names:
            button_title = self.get_button_title(intent, entities)
            buttons.append(
                {
                    "title": button_title,
                    "payload": f"/{intent}{entities_json}",
                }
            )

        buttons.append(
            {"title": "Something else!", "payload": "/trigger_rephrase"}
        )

        dispatcher.utter_message(text=message_title, buttons=buttons)

        return []

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
