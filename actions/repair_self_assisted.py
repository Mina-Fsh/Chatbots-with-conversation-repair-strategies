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


class ActionSelfAssistedRepair(Action):
    """This repair strategy uses different factors to explain
    the possible reasons behind the breakdown to the user."""

    def name(self) -> Text:
        return "action_self_assisted_repair"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:

        confusion_level = self.get_confusion_level(tracker)
        conversation_turns = self.count_turns(tracker)

        last_intent_name = self.get_user_message_info(tracker)[
            "last_intent_name"]
        last_user_message = self.get_user_message_info(tracker)[
            "last_user_message"]
        last_intent_confidence = self.get_user_message_info(tracker)[
            "last_intent_confidence"]
        second_last_intent_name = self.get_user_message_info(tracker)[
            "second_last_intent_name"]
        second_last_user_message = self.get_user_message_info(tracker)[
            "second_last_user_message"]
        second_last_intent_confidence = self.get_user_message_info(tracker)[
            "second_last_intent_confidence"]

        if second_last_intent_confidence is not None:
            # If the very first user message triggers fallback
            # there will be no second last intent
            if (last_intent_confidence >= 0.75 and
                    second_last_intent_confidence >= 0.75):
                # The last two user intents are probably recognized by the bot.
                # Here it is possible to mention the confusion level.
                logger.debug(f"The number of turns after restart is \
                {conversation_turns}. The confusion level is \
                {confusion_level}. The confidence levels are \
                {last_intent_confidence} and {second_last_intent_confidence}.")

                if confusion_level > 0:
                    # The bot is confused.
                    message_title = f"I don't know exactly what you mean by: \
                                {last_user_message}. Before that you said: \
                                {second_last_user_message}. I am not trained \
                                enough to handle switching between topics \
                                like this. I'm sorry."
                else:
                    # The bot is not confused. both last two
                    # intents have high confidence level.
                    # check turns? 
                    # 
                    logger.debug("")
                    message_title = ""
            elif (last_intent_confidence >= 0.75 and
                    second_last_intent_confidence < 0.75):
                # Bot is not so sure about the second last intent.
                # Here it is not possible to mention the confusion level.
                # Here we can mention user text length
                last_intent_category = self.get_intent_length_category(tracker)
                if last_intent_category == "long":
                    user_msg = tracker.latest_message['text']
                    user_msg_len = len(user_msg.split())
                    if user_msg_len < 3:
                        message_title = f"I don't know exactly what you mean by: \
                                {last_user_message}. I can help you better \
                                with more elaboration."
                    else:
                        message_title = f"Last intent category is long. User \
                            text length is {user_msg_len}"
                else:
                    message_title = f"Last intent category is short. User text \
                        length is {user_msg_len}"
            else:
                message_title = "This part should be coded!"
        else:
            message_title = "Second last intent confidence is None!"

        dispatcher.utter_message(text=message_title)

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
                "session_start"
                "human_handoff",
                "trigger_rephrase",
                "configure_repair_strategy"
            ],
            [
                "greet",
                "affirm",
                "deny",
                "bye",
                "telljoke",
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
                logger.debug(f"Intent {last_intent_name} is in {intent_group_index}.")
            else:
                intent_group_index = None

        intent_type = ""
        if intent_group_index == 0:
            intent_type == "long"
            logger.debug(f"Intent {last_intent_name} is in {intent_type}.")
        elif intent_group_index == 1:
            intent_type == "short"
            logger.debug(f"Intent {last_intent_name} is in {intent_type}.")
        else:
            logger.debug("Error in short long intent categorization.")

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
