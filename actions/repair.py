import logging
import requests
import random
from typing import Any, Dict, List, Text
from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import (
    SlotSet,
    EventType,
    FollowupAction,
)
from actions import config

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
                "title": "Fallback based on the bot confidence level.",
                "payload": "labelConfidencLevel",
            },
            {
                "title": "Fallback based on the user utterance length.",
                "payload": "labelUserUtteranceLenght",
            },
            {
                "title": "Fallback based on the bot's confusion and fatigue level.",
                "payload": "LabelFatigueConfusion",
            },
            {
                "title": "Fallback with options of highest ranked intents + recommending restart.",
                "payload": "twoStageOptions",
            },
            {
                "title": "Fallback with options of highest ranked intents.",
                "payload": "options",
            },
            {
                "title": "Randomly choose between the fallbacks above!",
                "payload": "random",
            },
            {
                "title": "Fallback that counts breakdowns and either gives options or utters the bot capabilities.",
                "payload": "countBreakdown",
            },
            {
                "title": "Fallback with recommending connection to a human agent.",
                "payload": "defer",
            },
            {
                "title": "Fallback with asking user to rephrase the request." ,
                "payload": "rephrase",
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
        logger.info(f'clause: { next((True for event in tracker.events[-15:] if event.get("name") == "action_repair"), False) }')

        repair_strategy = tracker.get_slot("repair_strategy_name")

        # Fallback caused by TwoStageFallbackPolicy
        if (
            len(tracker.events) >= 15 and 
            next((True for event in tracker.events[-15:] if event.get("name") == "action_repair" and repair_strategy == "twoStageOptions"), False)
        ):

            dispatcher.utter_message(template="utter_restart_with_button")

            return [
                SlotSet("feedback_value", "negative"),
            ]
        #######

        if repair_strategy == "rephrase":
            dispatcher.utter_message(template="utter_default")
        elif repair_strategy == "twoStageOptions":
            return [FollowupAction("action_repair_twoStageOptions")]
        elif repair_strategy == "options":
            return [FollowupAction("action_repair_options")]
        elif repair_strategy == "countBreakdown":
            return [FollowupAction("action_repair_count_breakdwon")]
        elif repair_strategy == "defer":
            message_title = "I'm sorry, but I didn't understand you.\n \
                I want to connect you to an agent but unfortunately there is \
                no agent available at the moment.\n Please contact the phone \
                number 01234567, or continue chatting with me! "
            dispatcher.utter_message(message_title)
        elif repair_strategy == "labelConfidencLevel":
            return [FollowupAction("action_repair_label_confidenc_level")]
        elif repair_strategy == "labelUserUtteranceLenght":
            return [FollowupAction("action_repair_label_user_utterance_length")]
        elif repair_strategy == "random":
            strategy_names = ["action_repair_label_confidenc_level",
                              "action_repair_label_user_utterance_length",
                              "action_repair_options",
                              "action_repair_label_fatigue_confusion"]
            random_strategy = random.choice(strategy_names)
            return [FollowupAction(random_strategy)]
        elif repair_strategy == "LabelFatigueConfusion":
            return [FollowupAction("action_repair_label_fatigue_confusion")]
        else:
            dispatcher.utter_message("I do not know this repair strategy")
        return []


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
