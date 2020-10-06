## out of scope
* out_of_scope
    - respond_out_of_scope

## say enter data outside the flows
* greet
    - action_greet_user
    - utter_intro
* inform
    - utter_not_sure
    - utter_intro

## say confirm outside the flows 2
* greet
    - action_greet_user
    - utter_intro
* affirm
    - utter_thumbsup

## say greet outside the flows
* greet
    - action_greet_user
    - utter_intro
* greet OR inform{"PERSON": "Nina"}
    - action_greet_user
    - utter_intro

## just search transactions + confirm
* greet
    - action_greet_user
    - utter_intro
* out_of_scope
    - respond_out_of_scope
* search_transactions OR check_earnings
    - transact_search_form
    - form{"name": "transact_search_form"}
    - form{"name": null}
    - utter_ask_feedback
* affirm
    - utter_thumbsup
    - utter_anything_else

## just search transactions, continue + confirm
* greet
    - action_greet_user
    - utter_intro
* search_transactions OR check_earnings
    - transact_search_form
    - form{"name": "transact_search_form"}
* out_of_scope
    - respond_out_of_scope
    - utter_ask_continue_transact_search
* affirm
    - utter_great
    - transact_search_form
    - form{"name": null}
    - utter_ask_feedback
* affirm
    - utter_thumbsup
    - utter_anything_else

## just search transactions, don't continue + confirm
* greet
    - action_greet_user
    - utter_intro
* search_transactions OR check_earnings
    - transact_search_form
    - form{"name": "transact_search_form"}
* out_of_scope
    - respond_out_of_scope
    - utter_ask_continue_transact_search
* deny
    - utter_thumbsup
    - action_deactivate_form
    - form{"name": null}
    - utter_ask_feedback
* affirm
    - utter_thumbsup
    - utter_anything_else