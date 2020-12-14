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


class ActionMixRepair(Action):
    """Responses to the user text based on it's confidency.
    if it is confidence it gives option, otherwise it checks for
    Fatigue and Multiple breakdowns"""

    def name(self) -> Text:
        return "action_mix_repair"

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

        conversation_turns = self.count_turns(tracker)
        last_user_message = self.get_user_message_info(tracker)[
            "last_user_message"]
        last_intent_confidence = self.get_user_message_info(tracker)[
            "last_intent_confidence"]
        last_intent_name = self.get_user_message_info(tracker)[
            "last_intent_name"]
        second_last_intent_confidence = self.get_user_message_info(tracker)[
            "second_last_intent_confidence"]
        buttons = []

        if second_last_intent_confidence is not None:
            # If the very first user message triggers fallback
            # there will be no second last intent
            if last_intent_confidence >= 0.75:
                # Bot is in breakdown with high CL
                # Confusion, user text length, fatigue or
                # multiple breakdowns can be relevant.
                message_title = "😊 I'm Highly confident that this is what you \
                    mean:"

                entities = tracker.latest_message.get("entities", [])
                entities = {e["entity"]: e["value"] for e in entities}

                entities_json = json.dumps(entities)

                button_title = self.get_button_title(last_intent_name,
                                                     entities)

                buttons.append(
                    {
                        "title": button_title,
                        "payload": f"/{last_intent_name}{entities_json}",
                    }
                )
                buttons.append(
                    {
                        "title": "Something else!",
                        "payload": "/trigger_rephrase"
                    }
                )
            else:
                # Bot is in breakdown with low CL
                # Confusion and user text length not relevant
                # Fatigue or multiple breakdowns can be relevant.
                if second_last_intent_confidence >= 0.9:
                    # fatigue can be relevant
                    if conversation_turns > 20:
                        # Fatigue
                        message_title = f"I don't know what you mean by: \
                        {last_user_message}. Eventhough we had a \
                        nice long conversation, I would like to \
                        have a coffee break."
                    else:
                        message_title = f"I don't know exactly what you mean by: \
                        {last_user_message}. Excuse me; I can't \
                        see what caused this breakdown. Maybe your request is \
                        out of my scope."
                else:
                    # Fatigue or multiple breakdowns can be relevant.
                    if conversation_turns > 20:
                        # Fatigue
                        message_title = f"I don't know what you mean by: \
                        {last_user_message}. Eventhough we had a \
                        nice long conversation, I would like to \
                        have a coffee break."
                    else:
                        # multiple breakdown
                        message_title = f"I don't know exactly what you mean by: \
                            {last_user_message}. I'm sorry that I \
                            wasn't able to help you in last two \
                            turns. \n \
                            I can help you with topics related to \
                            banking such as: \n- Transfer money to \
                            known recipients. \n- Check the earning \
                            or spending history. \n- Pay a credit \
                            card bill! \n- Tell the account balance. \
                            \n- Answer FAQ."
        else:
            # Very first user message caused breakdown.
            # Say Hi to the user
            message_title = "I'm afraid I didn't get what you just said. \
                Maybe we can start with saying Hi!"

        dispatcher.utter_message(text=message_title, buttons=buttons)

        return [FollowupAction("action_listen")]

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

    def get_user_utterance_length(
        self,
        tracker: Tracker
    ) -> int:

        user_msg = tracker.latest_message['text']
        user_msg_len = len(user_msg.split())
        logger.info(f"{user_msg}, {user_msg_len}")

        return user_msg_len

    def get_intent_length_category(
        self,
        tracker: Tracker
    ) -> Text:

        '''This functions gets returns short or long, as a category
        for intents.'''

        intent_list = [
            [
                "ask_builder",
                "ask_howbuilt",
                "ask_howdoing",
                "ask_howold",
                "ask_isbot",
                "ask_ishuman",
                "ask_languagesbot",
                "ask_restaurant",
                "ask_time",
                "ask_weather",
                "ask_whatismyname",
                "ask_wherefrom",
                "ask_whoami",
                "ask_whoisit",
                "handleinsult",
                "nicetomeetyou",
                "whatisPAYbank",
                "product_description",
                "howtoapply",
                "application_requirements",
                "required_age",
                "cardlimit",
                "points_collect",
                "annualcost",
                "transfer_money",
                "pay_cc",
                "ask_transfer_charge",
                "search_transactions",
                "check_balance",
                "check_earnings",
                "check_recipients",
                "capabilities",
                "session_start",
                "human_handoff",
                "trigger_rephrase",
                "telljoke",
                "configure_repair_strategy"
            ],
            [
                "greet",
                "affirm",
                "deny",
                "bye",
                "canthelp",
                "react_negative",
                "react_positive",
                "thank",
                "inform",
                "restart",
                "repeat"
            ]
        ]

        last_intent_name = self.get_user_message_info(tracker)[
            "last_intent_name"]

        for list in intent_list:
            if last_intent_name in list:
                intent_group_index = intent_list.index(list)
                logger.debug(f"Intent {last_intent_name} is\
                    in group index {intent_group_index}.")
                if intent_group_index == 0:
                    intent_type = "long"
                    logger.debug(f"Intent {last_intent_name} is in\
                        group category {intent_type}.")
                elif intent_group_index == 1:
                    intent_type = "short"
                    logger.debug(f"Intent {last_intent_name} is in\
                        group {intent_type}.")
                else:
                    intent_group_index = None
                    intent_type = None
                    logger.debug("Error in short long intent categorization.")
            else:
                logger.debug("Intent is not in the list of intents!")

        return intent_type

    def get_user_message_info(
            self,
            tracker: Tracker
    ) -> Dict[Text, Text]:

        '''This functions gets the name and the text from the last and
        second last user messages.'''

        user_event_list = []
        for events in tracker.events_after_latest_restart():
            if events["event"] == "user":
                user_event_list.append(events)

        # get the ranking of the last user message
        last_intent_ranking = user_event_list[-1].get(
            "parse_data", []).get("intent_ranking", [])

        # get the name of the matched intent for last user message
        last_intent_name = last_intent_ranking[0].get("name")
        # get the text of the last user message
        last_user_message = user_event_list[-1].get("text")
        # get the confidence level of the last user message
        last_intent_confidence = last_intent_ranking[0].get("confidence")

        # get the ranking of the second last user message
        if len(user_event_list) > 1:
            second_last_intent_ranking = user_event_list[-2].get(
                "parse_data", []).get("intent_ranking", [])
            # get the name of the matched intent for second last user message
            second_last_intent_name = second_last_intent_ranking[0].get("name")
            # get the text of the second last user message
            second_last_user_message = user_event_list[-2].get("text")
            # get the confidence level of the last user message
            second_last_intent_confidence = second_last_intent_ranking[0].get(
                "confidence")
        else:
            second_last_intent_name = None
            second_last_user_message = None
            second_last_intent_confidence = None

        return {
            "last_intent_name": last_intent_name,
            "last_user_message": last_user_message,
            "last_intent_confidence": last_intent_confidence,
            "second_last_intent_name": second_last_intent_name,
            "second_last_user_message": second_last_user_message,
            "second_last_intent_confidence": second_last_intent_confidence
            }

    def get_confusion_level(
        self,
        tracker: Tracker
    ) -> int:

        # Calculate confusion based on jumping from one intent to another
        # Grouping the intents based on their similarity in context
        distanced_intent_list = [
            [
                "greet",
                "bye",
                "nicetomeetyou",
                "restart",
                "ask_builder",
                "ask_howbuilt",
                "ask_isbot",
                "ask_ishuman",
                "ask_languagesbot",
                "ask_whoisit",
                "ask_howdoing",
                "ask_howold",
                "ask_wherefrom",
                "ask_whatismyname",
                "ask_whoami",
                "ask_restaurant",
                "ask_time",
                "ask_weather",
                "telljoke",
                "handleinsult"
            ],
            [
                "whatisPAYbank",
                "product_description",
                "howtoapply",
                "application_requirements",
                "required_age",
                "cardlimit",
                "points_collect",
                "annualcost"
            ],
            [
                "transfer_money",
                "pay_cc",
                "ask_transfer_charge",
                "search_transactions",
                "check_balance",
                "check_earnings",
                "check_recipients",
                "inform"
            ]
        ]

        last_intent_name = self.get_user_message_info(tracker)[
            "last_intent_name"]
        second_last_intent_name = self.get_user_message_info(tracker)[
            "second_last_intent_name"]

        for list in distanced_intent_list:
            if last_intent_name in list:
                index_1 = distanced_intent_list.index(list)
                logger.debug(f"{last_intent_name} is in \
                    group {index_1}.")
            else:
                index_1 = None

            if (second_last_intent_name is not None and
                    second_last_intent_name in list):
                index_2 = distanced_intent_list.index(list)
                logger.debug(f"{second_last_intent_name} is in \
                    group {index_2}.")
            else:
                index_2 = None

        confusion_level = 0
        logger.debug(f"index 1 is {index_1}")
        logger.debug(f"index 2 is {index_2}")

        if index_1 is not None and index_2 is not None:
            if index_1 != index_2:
                confusion_level += 1
                logger.debug(f"The confusion level is: {confusion_level}")

        return confusion_level

    def count_breakdowns(
            self,
            tracker: Tracker
    ) -> int:

        breakdown_counter = 0
        for events in tracker.events_after_latest_restart():
            if (events["event"] == "action" and
                    events["name"] == "action_repair"):
                breakdown_counter += 1

        logger.debug(f"You already had {breakdown_counter} \
        breakdowns in this conversation!")

        return breakdown_counter

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
