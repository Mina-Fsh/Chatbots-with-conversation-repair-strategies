import logging
import json
import requests
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


class ActionConfigureRepairStrategy(Action):

    def name(self) -> Text:
        return "action_configure_repair_strategy"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message_title = "Which repair strategy would you like to have in this conversation?"

        buttons = [
            {
                "title": "Ask to rephrase the request!" ,
                "payload": "rephrase",
            },
            {
                "title": "Show me options of highest ranked intents!",
                "payload": "options",
            },
            {
                "title": "In case of consecutive breakdowns, stop showing options to me!",
                "payload": "cumulative",
            },
            {
                "title": "Connect me to a human!",
                "payload": "defer",
            },
            {
                "title": "Tell me what you think I mean!",
                "payload": "labelConfidency",
            },
            {
                "title": "Decide based on the length of my utterances!",
                "payload": "labelUserUtteranceLenght",
            }
        ]

        dispatcher.utter_message(text=message_title, buttons=buttons)

        return []


class ActionRepair(Action):

    def name(self) -> Text:
        return "action_repair"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        repair_strategy = tracker.get_slot("repair_strategy_preferences")

        if repair_strategy == "rephrase":
            dispatcher.utter_message(template = "utter_default")
        elif repair_strategy == "options":
            return [FollowupAction("action_repair_options")]
        elif repair_strategy == "cumulative":
            return [FollowupAction("action_repair_count_breakdwon")]
        elif repair_strategy == "defer":
            message_title = "I'm sorry, but I didn't understand you.\n I want to connect you to an agent but unfortunately there is no agent available at the moment.\n Please contact the phone number 01234567, or continue chatting with me! "
            dispatcher.utter_message(message_title)
        elif repair_strategy == "labelConfidency":
            return [FollowupAction("action_repair_label_confidency")]
        elif repair_strategy == "labelUserUtteranceLenght":
            return [FollowupAction("action_repair_label_user_utterance_length")]
        else:
            dispatcher.utter_message("I do not know this repair strategy")
        return []


class ActionRepairLabelUserUtteranceLenght(Action):
    """Shows options in the first 5 sessions and after that asks for rephrase!"""

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
            message_title = "Dude I need some more explanation!"
        elif user_msg_len < 10 and  user_msg_len > 3:
            message_title = "🤐 Eventhough you elaborated your request nicely, I still couldn't get you. I'm sorry."
        else:
            message_title = "😵 You are talking a lot and it is confusing me dude!"

        dispatcher.utter_message(text=message_title)
        return []


class ActionRepairLabelConfidency(Action):
    """Shows options in the first 5 sessions and after that asks for rephrase!"""

    def name(self) -> Text:
        return "action_repair_label_confidency"
    
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
            if highest_ranked_intent_confidence > 0.7:
                message_title = "😊🧠 I'm Highly confident that this is what you mean:"
            elif highest_ranked_intent_confidence < 0.7 and  highest_ranked_intent_confidence > 0.6:
                message_title = "🙂 I'm somehow familiar whit this topic, I think you mean this:"
            elif highest_ranked_intent_confidence < 0.6 and  highest_ranked_intent_confidence > 0.4:
                message_title = "😕 You challenging me... I rely on my wisdom, you mean this:"
            elif highest_ranked_intent_confidence < 0.4 and  highest_ranked_intent_confidence > 0.1:
                message_title = "😵 You confusing me... maybe you mean this:"
            else:
                message_title = "🤥 You got me with this way of talking, my guess is probably:"
        
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

class ActionRepairOptions(Action):
    """Asks for an affirmation of the intent if NLU threshold is not met."""

    def name(self) -> Text:
        return "action_repair_options"

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
            diff_intent_confidence = intent_ranking[0].get(
                "confidence"
            ) - intent_ranking[1].get("confidence")
            if diff_intent_confidence < 0.2:
                intent_ranking = intent_ranking[:2]
            else:
                intent_ranking = intent_ranking[:1]

        # for the intent name used to retrieve the button title, we either use
        # the name of the name of the "main" intent, or if it's an intent that triggers
        # the response selector, we use the full retrieval intent name so that we
        # can distinguish between the different sub intents
        first_intent_names = [
            intent.get("name", "")
            if intent.get("name", "")
            not in ["faq", "chitchat"]
            else tracker.latest_message.get("response_selector")
            .get(intent.get("name", ""))
            .get("full_retrieval_intent")
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
            if "/" in intent:
                # here we use the button title as the payload as well, because you
                # can't force a response selector sub intent, so we need NLU to parse
                # that correctly
                buttons.append(
                    {"title": button_title, "payload": button_title}
                )
            else:
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

        if breakdown_counter <= 2:
            return [FollowupAction("action_repair_options")]
        elif breakdown_counter > 2:
            dispatcher.utter_message(template = "utter_capabilities_repair")
        return[]
    
class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:

        # Fallback caused by TwoStageFallbackPolicy
        if (
            len(tracker.events) >= 4
            and tracker.events[-4].get("name")
            == "action_repair_options"
        ):

            dispatcher.utter_message(template="utter_restart_with_button")

            return [
                SlotSet("feedback_value", "negative"),
                ConversationPaused(),
            ]

        # Fallback caused by Core
        else:
            dispatcher.utter_message(template="utter_default")
            return [UserUtteranceReverted()]


class ActionTagFeedback(Action):
    """Tag a conversation in Rasa X as positive or negative feedback """

    def name(self):
        return "action_tag_feedback"

    def run(self, dispatcher, tracker, domain) -> List[EventType]:

        feedback = tracker.get_slot("feedback_value")

        if feedback == "positive":
            label = '[{"value":"postive feedback","color":"76af3d"}]'
        elif feedback == "negative":
            label = '[{"value":"negative feedback","color":"ff0000"}]'
        else:
            return []

        tag_convo(tracker, label)

        return []


def tag_convo(tracker: Tracker, label: Text) -> None:
    """Tag a conversation in Rasa X with a given label"""
    endpoint = f"http://{config.rasa_x_host}/api/conversations/{tracker.sender_id}/tags"
    requests.post(url=endpoint, data=label)
    return
