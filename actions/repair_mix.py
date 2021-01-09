import logging
import json
from typing import Any, Dict, List, Text
from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import (
    SlotSet,
    EventType,
    FollowupAction,
)

INTENT_DESCRIPTION_MAPPING_PATH = "actions/intent_description_mapping.csv"

logger = logging.getLogger(__name__)


class ActionMixRepair(Action):
    """Responses to the user text based on it's confidency.
    if it is confidence it gives option, otherwise it checks for
    the technical reasons behind the breakdown."""

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

        last_user_message = self.get_user_message_info(tracker)[
            "last_user_message"]
        logger.info(f"last user message is: {last_user_message}")
        last_intent_name = self.get_user_message_info(tracker)[
            "last_intent_name"]
        logger.info(f"last intent name is: {last_intent_name}")
        last_intent_confidence = self.get_user_message_info(tracker)[
            "last_intent_confidence"]
        second_last_intent_confidence = self.get_user_message_info(tracker)[
            "second_last_intent_confidence"]

        confusion_level = self.get_confusion_level(tracker)
        logger.info(f"confusion level is: {confusion_level}")
        if confusion_level is True:
            confusion_warning = (
                "\n- In this conversation, we have switched between different topics. "
                "Which means we have taken off an expected conversation flow."
            )
        else:
            confusion_warning = ""

        conversation_turns = self.count_turns(tracker)
        logger.info(f"conv turns is: {conversation_turns}")
        if conversation_turns > 20:
            fatigue_warning = "\n- Our conversation has gotten too long, which means I have saved many keywords from our conversation history in my memory; this could mislead me."
        else:
            fatigue_warning = ""

        two_breakdowns_in_a_row = self.get_user_message_info(tracker)[
            "two_breakdowns_in_a_row"]
        logger.info(f"two breakdows is {two_breakdowns_in_a_row}")
        if two_breakdowns_in_a_row is True:
            multiple_breakdowns_warning = "\n- I have not understood your last two requests. The keywords you have used might have been unfamiliar to me."
        else:
            multiple_breakdowns_warning = ""

        number_of_breakdowns = self.count_breakdowns(tracker)
        logger.info(f"number of breakdowns: {number_of_breakdowns}")

        mean_std_dic = {}
        mean_std_dic = self.get_intent_mean_sd(
            tracker)
        last_intent_nlu_mean = mean_std_dic["mean"]
        last_intent_nlu_std = mean_std_dic["std"]
        user_msg_len = mean_std_dic["user_msg_len"]
        intent_description = self.get_intent_description(last_intent_name)

        if user_msg_len <= (last_intent_nlu_mean - 2 * (last_intent_nlu_std)):
            length_warning = f'\n- I have learned requests similar to "{intent_description}" with longer sentences containing more precise keywords.'
        elif user_msg_len >= (last_intent_nlu_mean + 2 * (last_intent_nlu_std)):
            length_warning = f'\n- I have learned requests similar to "{intent_description}" with shorter sentences containing less information.'
        else:
            length_warning = ""

        list_of_messages = [length_warning, fatigue_warning, confusion_warning, multiple_breakdowns_warning]
        if not any(s.strip() for s in list_of_messages):
            rephrase_mr_message = "Try to express your request in other words."
        else:
            rephrase_mr_message = "I think one of these can help you:" + length_warning + confusion_warning + fatigue_warning + multiple_breakdowns_warning + "\n Try to express your request in other words."

        logger.info(f"The message slot is: {rephrase_mr_message}")
        buttons = []

        if second_last_intent_confidence is not None:
            # If the very first user message triggers fallback
            # there will be no second last intent
            if last_intent_confidence >= 0.75:
                # Bot is in breakdown with high CL
                # Confusion, user text length, fatigue or
                # multiple breakdowns can be relevant.
                message_title = (
                    "Sorry, I'm not sure I've understood "
                    "you correctly 🤔 Do you mean..."
                )

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
                        "payload": "/trigger_rephrase_mr"
                    }
                )

            else:
                # Bot is in breakdown with low CL
                # Confusion and user text length not relevant
                # Fatigue or multiple breakdowns can be relevant.
                message = f"Sorry, I have severe doubts about what you mean by '{last_user_message}'.\n Here are the possible reasons behind this breakdown that comes to my mind: "
                message_two = "\n- Your request might be out of my scope. You can ask for my capabilities to get familiar with my skills."
                message_title = message + fatigue_warning + multiple_breakdowns_warning + message_two
        else:
            # Very first user message caused breakdown.
            # Say Hi to the user
            message_title = "I'm afraid I didn't get what you just said. Maybe we can start with saying Hi!"

        dispatcher.utter_message(text=message_title, buttons=buttons)

        return [SlotSet("rephrase_mr_message", rephrase_mr_message)]

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

        user_msg = self.get_user_message_info(tracker)[
            "last_user_message"]
        user_msg_len = len(user_msg.split())
        logger.info(f"User message is :{user_msg}, and the length is: {user_msg_len}")

        return user_msg_len

    def get_intent_mean_sd(
        self,
        tracker: Tracker
    ) -> Dict[Text, float]:

        '''This function gets the mean value and the
        standard deviation of the training data example lengths
        for an intent, it also removes the stop words from the user message'''

        import spacy
        import yaml
        import string
        import numpy as np  # for statistics
        import re  # for advanced string operations

        last_intent_name = self.get_user_message_info(tracker)[
            "last_intent_name"]

        with open('actions/nlu/nlu.yml') as file:
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

        # all_stopwords = nlp.Defaults.stop_words
        all_stopwords = spacy.lang.en.stop_words.STOP_WORDS

        example_lengths = []

        for example in clean_nlu_example_list:

            text_tokens = nlp(example)

            tokens_without_sw = [token.text for token in text_tokens if not token.is_stop]

            # tokens_without_sw = [word for word in text_tokens if not token.is_stop]

            logger.info(f"String without stopwords: {tokens_without_sw}")

            # count length of remaining example and store in list.

            length = len(tokens_without_sw)
            example_lengths.append(length) if (length > 0) else next

        logger.info(f"example length is: {example_lengths}")

        # calculate the mean value and the standard deviation of the list items
        # https://numpy.org/doc/stable/reference/generated/numpy.std.html#:~:text=The%20standard%20deviation%20is%20the,N%20%3D%20len(x)%20.

        mean = np.mean(example_lengths)

        std = np.std(example_lengths)

        logger.info(f"Mean: {mean}")
        logger.info(f"Standard deviation: {std}")

        user_msg = tracker.latest_message['text']
        user_text_tokens = nlp(user_msg)
        user_tokens_without_sw = [token.text for token in user_text_tokens if not token.is_stop]
        logger.info(f"User message without stopwords: {user_tokens_without_sw}")
        user_msg_len = len(user_tokens_without_sw)

        return {"mean": mean, "std": std, "user_msg_len": user_msg_len}

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
        # the first one in rasa 2 is always nlu_fallback
        last_intent_name = last_intent_ranking[1].get("name")
        # get the text of the last user message
        last_user_message = user_event_list[-1].get("text")
        # get the confidence level of the last user message
        last_intent_confidence = last_intent_ranking[1].get("confidence")

        # get the ranking of the second last user message
        # check for multiple breakdowns
        if len(user_event_list) > 1:
            second_last_intent_ranking = user_event_list[-2].get(
                "parse_data", []).get("intent_ranking", [])
            # get the name of the matched intent for second last user message
            # get the confidence level of the last user message
            if second_last_intent_ranking[0].get("name") == "nlu_fallback":
                second_last_intent_name = second_last_intent_ranking[1].get("name")
                second_last_intent_confidence = second_last_intent_ranking[1].get(
                    "confidence")
                two_breakdowns_in_a_row = True
            else:
                second_last_intent_name = second_last_intent_ranking[0].get("name")
                second_last_intent_confidence = second_last_intent_ranking[0].get(
                    "confidence")
                two_breakdowns_in_a_row = False

            # get the text of the second last user message
            second_last_user_message = user_event_list[-2].get("text")
        else:
            second_last_intent_name = None
            second_last_user_message = None
            second_last_intent_confidence = None
            two_breakdowns_in_a_row = False

        return {
            "last_intent_name": last_intent_name,
            "last_user_message": last_user_message,
            "last_intent_confidence": last_intent_confidence,
            "second_last_intent_name": second_last_intent_name,
            "second_last_user_message": second_last_user_message,
            "second_last_intent_confidence": second_last_intent_confidence,
            "two_breakdowns_in_a_row": two_breakdowns_in_a_row
                }

    def get_confusion_level(
        self,
        tracker: Tracker
    ) -> bool:

        # Calculate confusion based on jumping from one intent to another
        # Grouping the intents based on their similarity in context
        distanced_intent_list = [
            [
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

            if (second_last_intent_name is not None and second_last_intent_name in list):
                index_2 = distanced_intent_list.index(list)
                logger.debug(f"{second_last_intent_name} is in \
                    group {index_2}.")
            else:
                index_2 = None

        logger.debug(f"index 1 is {index_1}")
        logger.debug(f"index 2 is {index_2}")

        if index_1 is not None and index_2 is not None:
            confusion_level = True if index_1 != index_2 else False
        else:
            confusion_level = False

        return confusion_level

    def count_breakdowns(
            self,
            tracker: Tracker
    ) -> int:

        breakdown_counter = 0
        for events in tracker.events_after_latest_restart():
            if (events["event"] == "action" and events["name"] == "action_repair"):
                breakdown_counter += 1

        logger.debug(f"You already had {breakdown_counter} breakdowns in this conversation!")

        return breakdown_counter

    def get_intent_description(
        self, intent: Text
    ) -> Text:
        utterance_query = self.intent_mappings.intent == intent

        utterances = self.intent_mappings[utterance_query].button.tolist()

        if len(utterances) > 0:
            intent_description = utterances[0]
        else:
            utterances = self.intent_mappings[
                utterance_query
            ].button.tolist()
            intent_description = utterances[0] if len(utterances) > 0 else intent

        return intent_description.format()

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
