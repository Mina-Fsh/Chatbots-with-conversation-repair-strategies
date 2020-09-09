## chitchat
* chitchat
    - respond_chitchat

## deny chitchat
* chitchat
    - respond_chitchat
* deny
    - utter_nohelp

## more chitchat
* greet
    - action_greet_user
    - utter_intro
* chitchat
    - respond_chitchat
* chitchat
    - respond_chitchat

## greet chitchat
* greet
    - action_greet_user
    - utter_intro
* chitchat
    - respond_chitchat

## just check balance + confirm
* greet
    - action_greet_user
    - utter_intro
* chitchat
    - respond_chitchat
* check_balance
    - action_account_balance
    - utter_ask_feedback
* affirm
    - utter_thumbsup
    - utter_anything_else

## transaction search, continue, + confirm
* greet
    - action_greet_user
    - utter_intro
* search_transactions OR check_earnings
    - transact_search_form
    - form{"name": "transact_search_form"}
* chitchat
    - respond_chitchat
    - utter_ask_continue_transact_search
* affirm
    - utter_great
    - transact_search_form
    - form{"name": null}
    - utter_ask_feedback
* affirm
    - utter_thumbsup
    - utter_anything_else

## just transaction search, don't continue, + confirm
* greet
    - action_greet_user
    - utter_intro
* search_transactions OR check_earnings
    - transact_search_form
    - form{"name": "transact_search_form"}
* chitchat
    - respond_chitchat
    - utter_ask_continue_transact_search
* deny
    - utter_thumbsup
    - action_deactivate_form
    - form{"name": null}
    - utter_ask_feedback
* affirm
    - utter_thumbsup
    - utter_anything_else

## just transaction search
* greet
    - action_greet_user
    - utter_intro
* chitchat
    - respond_chitchat
* search_transactions OR check_earnings
    - transact_search_form
    - form{"name": "transact_search_form"}
    - form{"name": null}
    - utter_ask_feedback

## just transaction search, continue
* greet
    - action_greet_user
    - utter_intro
* search_transactions OR check_earnings
    - transact_search_form
    - form{"name": "transact_search_form"}
* chitchat
    - respond_chitchat
    - utter_ask_continue_transact_search
* affirm
    - utter_great
    - transact_search_form
    - form{"name": null}
    - utter_ask_feedback

## just newsletter, don't continue
* greet
    - action_greet_user
    - utter_intro
* search_transactions OR check_earnings
    - transact_search_form
    - form{"name": "transact_search_form"}
* chitchat
    - respond_chitchat
    - utter_ask_continue_transact_search
* deny
    - utter_thumbsup
    - action_deactivate_form
    - form{"name": null}
    - utter_ask_feedback

## just transfer money
* greet
    - action_greet_user
    - utter_intro
* chitchat
    - respond_chitchat
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
    - form{"name": null}
    - utter_ask_feedback

## just transfer money, continue
* greet
    - action_greet_user
    - utter_intro
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
* chitchat
    - respond_chitchat
    - utter_ask_continue_transfer
* affirm
    - utter_great
    - transfer_form
    - form{"name": null}

## just transfer money, don't continue
* greet
    - action_greet_user
    - utter_intro
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
* chitchat
    - respond_chitchat
    - utter_ask_continue_transfer
* deny
    - utter_thumbsup
    - action_deactivate_form