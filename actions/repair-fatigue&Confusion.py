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


class ActionRepairLabelFatigueConfusion(Action):
    """Shows options in the first 5
    sessions and after that asks for rephrase!"""

    def name(self) -> Text:
        return "action_repair_label_fatigue_confusion"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:

        # Calculate Fatigue based on the conversation lenght
        conv_turns = 0
        # conv_turns = tracker.get_slot("conv_turns")
        action_counter = 0
        user_event_list = []
        for events in tracker.events_after_latest_restart():

            if events["event"] == "user":
                user_event_list.append(events)
                conv_turns += 1

        # logger.debug(f"This is the tracker after restart:
        # {tracker.events_after_latest_restart()}")
        # logger.debug(f"There has been these events from
        # user so far: {user_event_list}")
        # logger.debug(f"There has been
        # {conv_turns} turns in this conversation so far!")

        # Calculate confusion based on jumping from one intent to another
        # Grouping the intents based on their similarity in context
        distanced_intent_list = [
            [
                "greet",
                "bye",
                "nicetomeetyou",
                "restart"
            ],
            [
                "ask_builder",
                "ask_howbuilt",
                "ask_isbot",
                "ask_ishuman",
                "ask_languagesbot"
            ],
            [
                "ask_whoisit",
                "ask_howdoing",
                "ask_howold",
                "ask_wherefrom"
            ],
            [
                "ask_whatismyname",
                "ask_whoami"
            ],
            [
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
                "affirm",
                "deny",
                "react_negative",
                "react_positive",
                "thank",
                "inform",
                "canthelp",
                "capabilities",
                "human_handoff",
                "configure_repair_strategy",
                "feedback"
            ],
            [
                "transfer_money",
                "pay_cc",
                "ask_transfer_charge",
                "search_transactions",
                "check_balance",
                "check_earnings",
                "check_recipients"
            ]]

        last_intent_ranking = user_event_list[-1].get(
            "parse_data", []).get("intent_ranking", [])
        last_intent_name = last_intent_ranking[0].get("name")

        last_user_message = user_event_list[-1].get("text")

        second_last_intent_ranking = user_event_list[-2].get(
            "parse_data", []).get("intent_ranking", [])
        second_last_intent_name = second_last_intent_ranking[0].get("name")

        second_last_user_message = user_event_list[-2].get("text")

        logger.debug(f"Last intent name is: {last_intent_name}, and the intent \
            before last is: {second_last_intent_name}")

        for list in distanced_intent_list:
            if last_intent_name in list:
                index_1 = distanced_intent_list.index(list)
                logger.debug(f"{last_intent_name} is in group {index_1}.")

            if second_last_intent_name in list:
                index_2 = distanced_intent_list.index(list)
                logger.debug(f"{second_last_intent_name} is in group {index_2}.")

        confusion_level = 0
        if index_1 != index_2:
            confusion_level += 1
            logger.debug(f"The confusion level is: {confusion_level}")

        # if conv_turns <= 6:
        #     return [FollowupAction("action_repair_options")]
        # elif conv_turns > 6:
        #     dispatcher.utter_message(template="utter_fatigue")
        #     return [FollowupAction("action_listen")]
        # return[]

        intent_ranking = tracker.latest_message.get("intent_ranking", [])
        if len(intent_ranking) > 1:
            highest_ranked_intent_confidence = intent_ranking[0].get(
                "confidence")
            highest_ranked_intent_name = intent_ranking[0].get("name")
            if highest_ranked_intent_confidence >= 0.75:
                if conv_turns <= 10:
                    # bot is not tired, and is somehow sure about the intent.
                    if confusion_level < 1:
                        # bot is not foncused
                        message_title = f"I'm Highly confident that you mean \
                            {last_intent_name}."
                    else:
                        # bot is confused
                        message_title = f"I'm Highly confident what you mean by: \
                            {last_user_message}. But before that you said: \
                             {second_last_user_message}. Switching between \
                             topics like this can confuse me in future. "
                else:
                    # bot is tired, and is somehow sure about the intent.
                    if confusion_level < 1:
                        # bot is not confused
                        message_title = f"I'm Highly confident what you mean by: \
                            {last_user_message}. But our conversation is \
                            getting long and I'm tired. Sorry."
                    else:
                        # bot is confused
                        message_title = f"I'm Highly confident what you mean by: \
                            {last_user_message}. But before that you said: \
                             {second_last_user_message}. Switching between \
                             topics like this can confuse me in future. \
                             Our conversation is also getting long \
                             and I'm tired. Sorry."
            else:
                if conv_turns <= 10:
                    # bot is not tired, and is not sure about the intent.
                    if confusion_level < 1:
                        # bot is not foncused
                        message_title = f"I'm not so sure about what you mean by: \
                            {last_user_message}."
                    else:
                        # bot is confused
                        message_title = f"I'm not so sure about what you mean by: \
                            {last_user_message}. But before that you said: \
                             {second_last_user_message}. Switching between \
                             these topics confused me."
                else:
                    # bot is tired, and is not sure about the intent.
                    if confusion_level < 1:
                        # bot is not confused
                        message_title = f"I'm not so sure about what you mean by: \
                            {last_user_message}. Our conversation is \
                            getting long and I'm tired. Maybe that's \
                            why I can't get you. Sorry."
                    else:
                        # bot is confused
                        message_title = f"I'm not so sure about what you mean by: \
                            {last_user_message}. But before that you said: \
                            {second_last_user_message}. Switching between \
                            these topics confused me. \
                            Our conversation is also getting long and I'm \
                            tired. Could be also why I can't get you. Sorry."

        dispatcher.utter_message(text=message_title)
        return [FollowupAction("action_listen")]
