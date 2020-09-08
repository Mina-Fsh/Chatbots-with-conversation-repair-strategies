## out of scope
* out_of_scope
    - respond_out_of_scope
    - utter_help

## say enter data outside the flows
* greet
    - action_greet_user
    - utter_help
* inform
    - utter_not_sure
    - utter_help

## say confirm outside the flows 2
* greet
    - action_greet_user
    - utter_help
* affirm
    - utter_thumbsup

## say greet outside the flows
* greet
    - action_greet_user
    - utter_help
* greet OR inform{"name": "akela"}
    - action_greet_user
    - utter_help

## just search transactions + confirm
* greet
    - action_greet_user
    - utter_help
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
    - utter_help
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
    - utter_help
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