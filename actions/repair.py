import logging
import random
from typing import Any, Dict, List, Text
from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import (
    SlotSet,
    FollowupAction,
)

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
                "title": "Based on the bot confidence level.",
                "payload": "labelConfidencLevel",
            },
            {
                "title": "Based on the bot's confusion and fatigue level.",
                "payload": "LabelFatigueConfusion",
            },
            {
                "title": "Give me options of highest ranked intents + rephrase \
                + recommend restart.",
                "payload": "twoStageOptions",
            },
            {
                "title": "Randomly choose between the above strategies!",
                "payload": "random",
            },
            {
                "title": "Give me options of highest ranked intents.",
                "payload": "options",
            },
            {
                "title": "Based on the user utterance length.",
                "payload": "labelUserUtteranceLenght",
            },
            {
                "title": "Give me options in the first 2 breakdowns, \
                after that it utters the bot capabilities.",
                "payload": "countBreakdown",
            },
            {
                "title": "Recommend connection to a human agent.",
                "payload": "defer",
            },
            {
                "title": "Ask me to rephrase my request.",
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
                              "action_repair_twoStageOptions",
                              "action_repair_label_fatigue_confusion"]
            random_strategy = random.choice(strategy_names)
            return [FollowupAction(random_strategy)]
        elif repair_strategy == "LabelFatigueConfusion":
            return [FollowupAction("action_repair_label_fatigue_confusion")]
        else:
            dispatcher.utter_message("I do not know this repair strategy")
        return []
