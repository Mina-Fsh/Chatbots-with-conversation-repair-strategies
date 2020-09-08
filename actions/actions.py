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
from dateutil import parser

INTENT_DESCRIPTION_MAPPING_PATH = "actions/intent_description_mapping.csv"

logger = logging.getLogger(__name__)


def custom_request_next_slot(
    form,
    dispatcher: "CollectingDispatcher",
    tracker: "Tracker",
    domain: Dict[Text, Any],
) -> Optional[List[EventType]]:
    """Request the next slot and utter template if needed,
        else return None"""

    for slot in form.required_slots(tracker):
        if form._should_request_slot(tracker, slot):
            logger.debug(f"Request next slot '{slot}'")
            dispatcher.utter_message(
                template=f"utter_ask_{form.name()}_{slot}", **tracker.slots
            )
            return [SlotSet(REQUESTED_SLOT, slot)]

    return None


class PayCCForm(FormAction):
    """Pay credit card form..."""

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "cc_payment_form"

    def request_next_slot(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[Text, Any],
    ) -> Optional[List[EventType]]:

        return custom_request_next_slot(self, dispatcher, tracker, domain)

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["credit_card", "payment_amount", "time", "confirm"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {
            "payment_amount": [
                self.from_entity(entity="payment_amount"),
                self.from_entity(entity="amount-of-money"),
                self.from_entity(entity="number"),
            ],
            "confirm": [
                self.from_intent(value=True, intent="affirm"),
                self.from_intent(value=False, intent="deny"),
            ],
        }

    def validate_payment_amount(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate payment amount value."""

        credit_card = tracker.get_slot("credit_card")
        cc_balance = tracker.get_slot("credit_card_balance")
        account_balance = float(tracker.get_slot("account_balance"))
        try:
            entity = get_entity_details(
                tracker, "amount-of-money"
            ) or get_entity_details(tracker, "number")
            amount_currency = parse_duckling_currency(entity)
            if not amount_currency:
                raise (TypeError)
            if account_balance < float(amount_currency.get("amount_of_money")):
                dispatcher.utter_message(template="utter_insufficient_funds")
                return {"payment_amount": None}
            return amount_currency
        except (TypeError, AttributeError):
            pass
        if value and value.lower() in cc_balance.get(credit_card.lower()):
            key = value.lower()
            amount = cc_balance.get(credit_card.lower()).get(key)
            amount_type = f" (your {key})"

            if account_balance < float(amount):
                dispatcher.utter_message(template="utter_insufficient_funds")
                return {"payment_amount": None}
            return {
                "payment_amount": f"{amount:.2f}",
                "payment_amount_type": amount_type,
                "currency": "$",
            }

        else:
            dispatcher.utter_message(template="utter_no_payment_amount")
            return {"payment_amount": None}

    def validate_credit_card(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate credit_card value."""

        cc_balance = tracker.get_slot("credit_card_balance")
        if value and value.lower() in list(cc_balance.keys()):
            return {"credit_card": value.title()}
        else:
            dispatcher.utter_message(template="utter_no_creditcard")
            return {"credit_card": None}

    def validate_time(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate time value."""

        timeentity = get_entity_details(tracker, "time")
        parsedtime = parse_duckling_time(timeentity)
        if not parsedtime:
            dispatcher.utter_message(template="utter_no_transactdate")
            return {"time": None}
        return parsedtime

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        account_balance = float(tracker.get_slot("account_balance"))
        credit_card = tracker.get_slot("credit_card")
        cc_balance = tracker.get_slot("credit_card_balance")
        payment_amount = float(tracker.get_slot("payment_amount"))
        amount_transferred = float(tracker.get_slot("amount_transferred"))

        if tracker.get_slot("confirm"):
            cc_balance[credit_card.lower()][
                "current balance"
            ] -= payment_amount
            account_balance = account_balance - payment_amount
            dispatcher.utter_message(template="utter_cc_pay_scheduled")

            return [
                SlotSet("credit_card", None),
                SlotSet("payment_amount", None),
                SlotSet("confirm", None),
                SlotSet("time", None),
                SlotSet("time_formatted", None),
                SlotSet("start_time", None),
                SlotSet("end_time", None),
                SlotSet("start_time_formatted", None),
                SlotSet("end_time_formatted", None),
                SlotSet("grain", None),
                SlotSet("amount_of_money", None),
                SlotSet(
                    "amount_transferred", amount_transferred + payment_amount,
                ),
                SlotSet("account_balance", f"{account_balance:.2f}"),
                SlotSet("credit_card_balance", cc_balance),
            ]
        else:
            dispatcher.utter_message(template="utter_cc_pay_cancelled")

        return [
            SlotSet("credit_card", None),
            SlotSet("payment_amount", None),
            SlotSet("confirm", None),
            SlotSet("time", None),
            SlotSet("time_formatted", None),
            SlotSet("start_time", None),
            SlotSet("end_time", None),
            SlotSet("start_time_formatted", None),
            SlotSet("end_time_formatted", None),
            SlotSet("grain", None),
        ]


class TransactSearchForm(FormAction):
    """Transaction search form"""

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "transact_search_form"

    def request_next_slot(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[Text, Any],
    ) -> Optional[List[EventType]]:

        return custom_request_next_slot(self, dispatcher, tracker, domain)

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["search_type", "time"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {
            "search_type": [
                self.from_trigger_intent(
                    intent="search_transactions", value="spend"
                ),
                self.from_trigger_intent(
                    intent="check_earnings", value="deposit"
                ),
            ],
        }

    def validate_vendor_name(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate vendor_name value."""

        if value and value.lower() in tracker.get_slot("vendor_list"):
            return {"vendor_name": value}
        else:
            dispatcher.utter_message(template="utter_no_vendor_name")
            return {"vendor_name": None}

    def validate_time(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate time value."""
        timeentity = get_entity_details(tracker, "time")
        parsedinterval = parse_duckling_time_as_interval(timeentity)
        if not parsedinterval:
            dispatcher.utter_message(template="utter_no_transactdate")
            return {"time": None}

        return parsedinterval

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        search_type = tracker.get_slot("search_type")
        transaction_history = tracker.get_slot("transaction_history")
        transactions_subset = transaction_history.get(search_type, {})
        vendor = tracker.get_slot("vendor_name")

        if vendor:
            transactions = transactions_subset.get(vendor.lower())
            vendor = f" with {vendor}"
        else:
            transactions = [
                v for k in list(transactions_subset.values()) for v in k
            ]
            vendor = ""

        start_time = parser.isoparse(tracker.get_slot("start_time"))
        end_time = parser.isoparse(tracker.get_slot("end_time"))

        for i in range(len(transactions) - 1, -1, -1):
            transaction = transactions[i]
            transaction_date = parser.isoparse(transaction.get("date"))

            if transaction_date < start_time or transaction_date > end_time:
                transactions.pop(i)

        numtransacts = len(transactions)
        total = sum([t.get("amount") for t in transactions])
        slotvars = {
            "total": f"{total:.2f}",
            "numtransacts": numtransacts,
            "start_time_formatted": tracker.get_slot("start_time_formatted"),
            "end_time_formatted": tracker.get_slot("end_time_formatted"),
            "vendor_name": vendor,
        }

        dispatcher.utter_message(
            template=f"utter_searching_{search_type}_transactions", **slotvars
        )
        dispatcher.utter_message(
            template=f"utter_found_{search_type}_transactions", **slotvars
        )

        return [
            SlotSet("time", None),
            SlotSet("time_formatted", None),
            SlotSet("start_time", None),
            SlotSet("end_time", None),
            SlotSet("start_time_formatted", None),
            SlotSet("end_time_formatted", None),
            SlotSet("grain", None),
            SlotSet("search_type", None),
            SlotSet("vendor_name", None),
        ]


class TransferForm(FormAction):
    """Transfer money form..."""

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "transfer_form"

    def request_next_slot(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[Text, Any],
    ) -> Optional[List[EventType]]:

        return custom_request_next_slot(self, dispatcher, tracker, domain)

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["PERSON", "amount_of_money", "confirm"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {
            "amount_of_money": [
                self.from_entity(entity="amount-of-money"),
                self.from_entity(entity="number"),
            ],
            "confirm": [
                self.from_intent(value=True, intent="affirm"),
                self.from_intent(value=False, intent="deny"),
            ],
        }

    def validate_PERSON(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        name = value.title() if value else None
        known_recipients = tracker.get_slot("known_recipients")
        first_names = [name.split()[0] for name in known_recipients]
        if name in known_recipients:
            return {"PERSON": name}
        elif name in first_names:
            index = first_names.index(name)
            fullname = known_recipients[index]
            return {"PERSON": fullname}
        else:
            dispatcher.utter_message(template="utter_unknown_recipient")
            return {"PERSON": None}

    def validate_amount_of_money(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        account_balance = float(tracker.get_slot("account_balance"))
        try:
            entity = get_entity_details(
                tracker, "amount-of-money"
            ) or get_entity_details(tracker, "number")
            amount_currency = parse_duckling_currency(entity)
            if not amount_currency:
                raise (TypeError)
            if account_balance < float(amount_currency.get("amount_of_money")):
                dispatcher.utter_message(template="utter_insufficient_funds")
                return {"amount_of_money": None}
            return amount_currency
        except (TypeError, AttributeError):
            dispatcher.utter_message(template="utter_no_payment_amount")
            return {"amount_of_money": None}

    def submit(self, dispatcher, tracker, domain):
        if tracker.get_slot("confirm"):
            amount_of_money = float(tracker.get_slot("amount_of_money"))
            account_balance = float(tracker.get_slot("account_balance"))

            updated_account_balance = account_balance - amount_of_money

            dispatcher.utter_message(template="utter_transfer_complete")

            amount_transferred = tracker.get_slot("amount_transferred")
            return [
                SlotSet("PERSON", None),
                SlotSet("amount_of_money", None),
                SlotSet("confirm", None),
                SlotSet(
                    "amount_transferred", amount_transferred + amount_of_money
                ),
                SlotSet("account_balance", f"{updated_account_balance:.2f}"),
            ]
        else:
            dispatcher.utter_message(template="utter_transfer_cancelled")
            return [
                SlotSet("PERSON", None),
                SlotSet("amount_of_money", None),
                SlotSet("confirm", None),
            ]


class ActionAccountBalance(Action):
    def name(self):
        return "action_account_balance"

    def run(self, dispatcher, tracker, domain):
        account_balance = float(tracker.get_slot("account_balance"))
        amount = tracker.get_slot("amount_transferred")
        if amount:
            amount = float(tracker.get_slot("amount_transferred"))
            init_account_balance = account_balance + amount
            dispatcher.utter_message(
                template="utter_changed_account_balance",
                init_account_balance=f"{init_account_balance:.2f}",
                account_balance=f"{account_balance:.2f}",
            )
            return [SlotSet("payment_amount", None)]
        else:
            dispatcher.utter_message(
                template="utter_account_balance",
                init_account_balance=f"{account_balance:.2f}",
            )
            return [SlotSet("payment_amount", None)]


class ActionCreditCardBalance(Action):
    def name(self):
        return "action_credit_card_balance"

    def run(self, dispatcher, tracker, domain):
        credit_card_balance = tracker.get_slot("credit_card_balance")
        credit_card = tracker.get_slot("credit_card")

        if credit_card and credit_card.lower() in credit_card_balance:
            current_balance = credit_card_balance[credit_card.lower()][
                "current balance"
            ]
            dispatcher.utter_message(
                template="utter_credit_card_balance",
                credit_card=credit_card.title(),
                amount_of_money=f"{current_balance:.2f}",
            )
            return [SlotSet("credit_card", None)]
        else:
            for credit_card in credit_card_balance.keys():
                current_balance = credit_card_balance[credit_card][
                    "current balance"
                ]
                dispatcher.utter_message(
                    template="utter_credit_card_balance",
                    credit_card=credit_card.title(),
                    amount_of_money=f"{current_balance:.2f}",
                )

            return []


class ActionRecipients(Action):
    def name(self):
        return "action_recipients"

    def run(self, dispatcher, tracker, domain):
        recipients = tracker.get_slot("known_recipients")
        formatted_recipients = "\n" + "\n".join(
            [f"- {recipient}" for recipient in recipients]
        )
        dispatcher.utter_message(
            template="utter_recipients",
            formatted_recipients=formatted_recipients,
        )
        return []


class ActionSessionStart(Action):
    def name(self) -> Text:
        return "action_session_start"

    @staticmethod
    def _slot_set_events_from_tracker(tracker: "Tracker",) -> List["SlotSet"]:
        """Fetch SlotSet events from tracker and carry over keys and values"""

        return [
            SlotSet(key=event.get("name"), value=event.get("value"),)
            for event in tracker.events
            if event.get("event") == "slot"
        ]

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:

        # the session should begin with a `session_started` event
        events = [SessionStarted()]

        events.extend(self._slot_set_events_from_tracker(tracker))

        # create mock profile
        user_profile = create_mock_profile()

        # initialize slots from mock profile
        for key, value in user_profile.items():
            if value is not None:
                events.append(SlotSet(key=key, value=value))

        # an `action_listen` should be added at the end
        events.append(ActionExecuted("action_listen"))

        return events


class ActionRestart(Action):
    def name(self) -> Text:
        return "action_restart"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:

        return [Restarted(), FollowupAction("action_session_start")]


class ActionPause(Action):
    """Pause the conversation"""

    def name(self) -> Text:
        return "action_pause"

    def run(self, dispatcher, tracker, domain) -> List[EventType]:
        return [ConversationPaused()]

class ActionGreetUser(Action):
    """Greets the user with/without privacy policy"""

    def name(self) -> Text:
        return "action_greet_user"

    def run(self, dispatcher, tracker, domain) -> List[EventType]:
        intent = tracker.latest_message["intent"].get("name")
        name_entity = next(tracker.get_latest_entity_values("name"), None)
        if intent == "greet" or (intent == "enter_data" and name_entity):
            dispatcher.utter_message(template="utter_greet_name", name=name_entity)
            return []
        else:
            dispatcher.utter_message(template="utter_greet_noname")
            return []


class ActionDefaultAskAffirmation(Action):
    """Asks for an affirmation of the intent if NLU threshold is not met."""

    def name(self) -> Text:
        return "action_default_ask_affirmation"

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
            not in ["out_of_scope", "faq", "chitchat"]
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
            {"title": "Connect me to a human agent", "payload": "/trigger_handoff"}
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
            == "action_default_ask_affirmation"
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