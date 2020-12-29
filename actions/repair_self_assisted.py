import logging
from typing import Any, Dict, List, Text
from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import (
    EventType,
    FollowupAction,
)

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

        last_user_message = self.get_user_message_info(tracker)[
            "last_user_message"]
        last_intent_name = self.get_user_message_info(tracker)[
            "last_intent_name"]
        logger.info(f"last intent name is: {last_intent_name}")
        last_intent_confidence = self.get_user_message_info(tracker)[
            "last_intent_confidence"]
        second_last_user_message = self.get_user_message_info(tracker)[
            "second_last_user_message"]
        second_last_intent_confidence = self.get_user_message_info(tracker)[
            "second_last_intent_confidence"]

        if second_last_intent_confidence is not None:
            # If the very first user message triggers fallback
            # there will be no second last intent
            if last_intent_confidence >= 0.75:
                # Bot is in breakdown with high CL
                # Confusion, user text length, fatigue or
                # multiple breakdowns can be relevant.
                if second_last_intent_confidence >= 0.9:
                    # Bot was not in breakdown is second last intent
                    # Multiple breakdowns not relevant.
                    # Confusion, user text length or fatigue can be relevant.
                    if confusion_level > 0:
                        # The bot is confused.
                        message_title = f"I'm not compeletely sure what you mean by: \
                            {last_user_message}. Before that you said: \
                            {second_last_user_message}. I am not trained \
                            enough to handle switching between topics \
                            like this. I'm sorry."
                    else:
                        # Bot is not confused.
                        # user text length or fatigue can be relevant.
                        # First check user text lenght
                        last_intent_nlu_mean = self.get_intent_mean_sd(
                            tracker)["mean"]
                        last_intent_nlu_std = self.get_intent_mean_sd(
                            tracker)["std"]
                        user_msg = tracker.latest_message['text']
                        user_msg_len = len(user_msg.split())

                        if user_msg_len <= (last_intent_nlu_mean - 2 * (last_intent_nlu_std)):
                            message_title = f"I don't know exactly what you mean by: \
                                {last_user_message}. I am trained on longer examples \
                                for similar requests."
                        elif user_msg_len >= (last_intent_nlu_mean + 2 * (last_intent_nlu_std)):
                            message_title = f"I don't know exactly what you mean by: \
                                {last_user_message}. I am trained on shorter examples \
                                for similar requests."
                        elif conversation_turns > 20:
                            # user text length is ok
                            # check fatigue
                            # Fatigue can be relevant
                            message_title = f"I don't know exactly what you mean by: \
                                {last_user_message}. Eventhough we had a \
                                nice long conversation, I would like to \
                                have a coffee break."
                        else:
                            message_title = f"I don't know exactly what you mean by: \
                                {last_user_message}. Excuse me; I can't \
                                see what caused this breakdown."
                elif 0.75 <= second_last_intent_confidence < 0.9:
                    # Bot has had two breakdowns in a row with high CL
                    # Multiple breakdowns, confusion, user text length or
                    # fatigue can be relevant.
                    if confusion_level > 0:
                        # The bot is confused.
                        message_title = f"I'm not compeletely sure what you mean by: \
                            {last_user_message}. Before that you said: \
                            {second_last_user_message}. I am not trained \
                            enough to handle switching between topics \
                            like this. I'm sorry."
                    else:
                        # Bot is not confused.
                        # user text length , fatigue or multiple breakdown
                        # can be relevant.
                        # First check user text lenght
                        last_intent_nlu_mean = self.get_intent_mean_sd(
                            tracker)["mean"]
                        last_intent_nlu_std = self.get_intent_mean_sd(
                            tracker)["std"]
                        user_msg = tracker.latest_message['text']
                        user_msg_len = len(user_msg.split())

                        if user_msg_len <= (last_intent_nlu_mean - 2 * (last_intent_nlu_std)):
                            message_title = f"I don't know exactly what you mean by: \
                                {last_user_message}. I am trained on longer examples \
                                for similar requests."
                        elif user_msg_len >= (last_intent_nlu_mean + 2 * (last_intent_nlu_std)):
                            message_title = f"I don't know exactly what you mean by: \
                                {last_user_message}. I am trained on shorter examples \
                                for similar requests."
                        elif conversation_turns > 20:
                            # user text length is ok
                            # check fatigue
                            # Fatigue can be relevant
                            message_title = f"I don't know exactly what you mean by: \
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

    def get_intent_mean_sd(
        self,
        tracker: Tracker
    ) -> Dict[Text, float]:

        '''This functions gets the mean value and the
        standard deviation of the training data example lengths
        for an intent'''

        import spacy
        import yaml
        import string
        import numpy as np # for statistics
        import re # for advanced string operations

        last_intent_name = self.get_user_message_info(tracker)[
            "last_intent_name"]

        with open('data/nlu/nlu.yml') as file:
            # The FullLoader parameter handles the conversion from YAML
            # scalar values to Python the dictionary format
            nlu_dic = yaml.load(file, Loader=yaml.FullLoader)
            nlu_list = nlu_dic["nlu"]
            res = next((sub for sub in nlu_list if sub['intent'] == last_intent_name), None)
            intent_nlu_examples = res["examples"]
            logger.info(f"{res}")
            logger.info(f"Intent examples: {intent_nlu_examples}")

        nlp = spacy.load("en_core_web_sm")
        doc = nlp(intent_nlu_examples)

        # for chunk in doc.noun_chunks:
        # logger.info(chunk.text, chunk.root.text, chunk.root.dep_,
        #       chunk.root.head.text)

        # clean string from annotations
        # https://stackabuse.com/using-regex-for-text-manipulation-in-python/
        # https://regexr.com/ 

        annotation_pattern = "\(.*\)|\{.*\}"

        cleaned_string = re.sub(annotation_pattern, "", intent_nlu_examples)

        logger.info(f"NLU example string without annotations: {cleaned_string}")

        # split string
        nlu_example_list = cleaned_string.split("- ")

        logger.info(f"NLU example list: {nlu_example_list}")

        # clean string

        # remove examples with empty strings from the list.
        clean_nlu_example_list = [x for x in nlu_example_list if x]

        # remove line breaks for each example string.
        clean_nlu_example_list = [x.replace('\n', ' ').replace('\r', '') for x in clean_nlu_example_list]

        logger.info(f"Clean NLU example list: {clean_nlu_example_list}")

        list = []

        # removes all punctuations in the example string.
        # https://stackoverflow.com/questions/265960/best-way-to-strip-punctuation-from-a-string
        for example in clean_nlu_example_list:
            result = example.translate(str.maketrans('', '', string.punctuation))
            list.append(result)

        clean_nlu_example_list = list

        logger.info(f"No punctuation NLU example list: {clean_nlu_example_list}")

        # remove stop words
        # https://stackabuse.com/removing-stop-words-from-strings-in-python/#usingthespacylibrary 

        all_stopwords = nlp.Defaults.stop_words

        example_lengths = []

        for example in clean_nlu_example_list:

            text_tokens = nlp(example)

            tokens_without_sw = [word for word in text_tokens if not word in all_stopwords]

            logger.info(f"String without stopwords: {tokens_without_sw}")

            # count length of remaining example and store in list.

            length = len(tokens_without_sw)
            example_lengths.append(length)

            logger.info(f"example length is: {example_lengths}")

        # calculate the mean value and the standard deviation of the list items
        # https://numpy.org/doc/stable/reference/generated/numpy.std.html#:~:text=The%20standard%20deviation%20is%20the,N%20%3D%20len(x)%20.

        mean = np.mean(example_lengths)

        std = np.std(example_lengths)

        logger.info(f"Mean: {mean}")
        logger.info(f"Standard deviation: {std}")

        return {"mean": mean, "std": std}

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
