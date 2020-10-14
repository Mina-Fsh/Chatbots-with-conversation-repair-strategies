## greet/bye path
* greet
    - action_greet_user
    - utter_intro

## configure repair stategy
* configure_repair_strategy
    - action_configure_repair_strategy
* inform{"repair_strategy_preferences": "options"}
    - utter_repair_strategy_saved
    - utter_ask_feedback

## thanks
* thank
    - utter_noworries
    - utter_anything_else

## bye
* bye
    - utter_bye

## restart
* restart
    - action_restart

## capability check
* capabilities
    - utter_capabilities

## greet
* greet OR inform{"PERSON": "akela"}
    - action_greet_user

## anything else? - yes
    - utter_anything_else
* affirm
    - utter_what_help

## anything else? - no
    - utter_anything_else
* deny
    - utter_thumbsup
    - utter_ask_feedback

## positive reaction
* react_positive
    - utter_react_positive
    - utter_ask_feedback

## negative reaction
* react_negative
    - utter_react_negative
    - utter_ask_feedback

## neither 
* greet
    - action_greet_user
    - utter_intro
* deny
    - utter_nohelp

## pay credit card no greet or thanks
* pay_cc
    - cc_payment_form
    - form{"name": "cc_payment_form"}
    - form{"name": null}
    - utter_ask_feedback

## pay credit card and check account balance
* pay_cc
    - cc_payment_form
    - form{"name": "cc_payment_form"}
    - form{"name": null}
* check_balance
    - action_account_balance
    - utter_ask_feedback

## pay credit card and check account balance inside form
* pay_cc
    - cc_payment_form
    - form{"name": "cc_payment_form"}
* check_balance
    - action_account_balance
    - utter_ask_continue
* affirm
    - cc_payment_form
    - form{"name": null}
    - utter_ask_feedback

## transfer money
* transfer_money
    - transfer_form
    - form{"name": "transfer_form"}
    - form{"name": null}
    - utter_ask_feedback

## is there a transfer charge
* ask_transfer_charge
    - utter_transfer_charge
    - utter_ask_feedback

## transfer money ask transfer charge
* transfer_money
    - transfer_form
    - form{"name": "transfer_form"}
* ask_transfer_charge
    - utter_transfer_charge
    - transfer_form
    - form{"name": "transfer_form"}
    - form{"name": null}
    - utter_ask_feedback
  
## transfer money ask known recipients
* transfer_money
    - transfer_form
    - form{"name": "transfer_form"}
* check_recipients
    - action_recipients
    - transfer_form
    - form{"name": "transfer_form"}
    - form{"name": null}
    - utter_ask_feedback

## transfer money ask known recipients and transfer charge
* transfer_money
    - transfer_form
    - form{"name": "transfer_form"}
* check_recipients
    - action_recipients
    - transfer_form
    - form{"name": "transfer_form"}
* ask_transfer_charge
    - utter_transfer_charge
    - transfer_form
    - form{"name": "transfer_form"}
    - form{"name": null}
    - utter_ask_feedback

## transfer money ask known recipients and transfer charge
* transfer_money
    - transfer_form
    - form{"name": "transfer_form"}
* ask_transfer_charge
    - utter_transfer_charge
    - transfer_form
    - form{"name": "transfer_form"}
* check_recipients
    - action_recipients
    - transfer_form
    - form{"name": "transfer_form"}
    - form{"name": null}
    - utter_ask_feedback

## transfer money ask account balance
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
* check_balance
    - action_account_balance
    - transfer_form
    - form{"name": "transfer_form"}
    - form{"name":null}
    - slot{"requested_slot":null}
    - utter_ask_feedback

## transfer money ask account balance
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
* check_balance
    - action_account_balance
    - transfer_form
    - form{"name": "transfer_form"}
* ask_transfer_charge
    - utter_transfer_charge
    - transfer_form
    - form{"name": "transfer_form"}
* check_recipients
    - action_recipients
    - transfer_form
    - form{"name": "transfer_form"}
    - form{"name":null}
    - slot{"requested_slot":null}
    - utter_ask_feedback

## transfer money ask account balance
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
* ask_transfer_charge
    - utter_transfer_charge
    - transfer_form
    - form{"name": "transfer_form"}
* check_balance
    - action_account_balance
    - transfer_form
    - form{"name": "transfer_form"}
* check_recipients
    - action_recipients
    - transfer_form
    - form{"name": "transfer_form"}
    - form{"name":null}
    - slot{"requested_slot":null}
    - utter_ask_feedback

## transfer money ask account balance
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
* check_recipients
    - action_recipients
    - transfer_form
    - form{"name": "transfer_form"}
* ask_transfer_charge
    - utter_transfer_charge
    - transfer_form
    - form{"name": "transfer_form"}
* check_balance
    - action_account_balance
    - transfer_form
    - form{"name": "transfer_form"}
    - form{"name":null}
    - slot{"requested_slot":null}
    - utter_ask_feedback

## transfer money ask account balance
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
* ask_transfer_charge
    - utter_transfer_charge
    - transfer_form
    - form{"name": "transfer_form"}
* check_recipients
    - action_recipients
    - transfer_form
    - form{"name": "transfer_form"}
* check_balance
    - action_account_balance
    - transfer_form
    - form{"name": "transfer_form"}
    - form{"name":null}
    - slot{"requested_slot":null}
    - utter_ask_feedback

## transfer money ask account balance
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
* check_recipients
    - action_recipients
    - transfer_form
    - form{"name": "transfer_form"}
* check_balance
    - action_account_balance
    - transfer_form
    - form{"name": "transfer_form"} 
* ask_transfer_charge
    - utter_transfer_charge
    - transfer_form
    - form{"name": "transfer_form"}
    - form{"name":null}
    - slot{"requested_slot":null}
    - utter_ask_feedback

## search transactions happy path
* greet
    - action_greet_user
    - utter_intro
* search_transactions
    - transact_search_form
    - form{"name": "transact_search_form"}
    - form{"name": null}
    - utter_ask_feedback


## search transactions happy path no greet
* search_transactions
    - transact_search_form
    - form{"name": "transact_search_form"}
    - form{"name": null}
    - utter_ask_feedback
* thank
    - utter_noworries
    - utter_anything_else

## search transactions happy path no greet or thanks
* search_transactions OR check_earnings
    - transact_search_form
    - form{"name": "transact_search_form"}
    - form{"name": null}
    - utter_ask_feedback

## search transactions switch to transfer money
* search_transactions OR check_earnings
    - transact_search_form
    - form{"name": "transact_search_form"}
* transfer_money
    - utter_ask_switch_goal
* affirm
    - transfer_form
    - form{"name": "transfer_form"}
    - form{"name": null}
    - utter_ask_back_to_transact
* affirm
    - transact_search_form
    - form{"name": "transact_search_form"}
    - form{"name": null}
    - utter_ask_feedback

## search transactions switch to transfer money, deny
* search_transactions OR check_earnings
    - transact_search_form
    - form{"name": "transact_search_form"}
* transfer_money
    - utter_ask_switch_goal
* deny
    - transact_search_form
    - form{"name": "transact_search_form"}
    - form{"name": null}
    - utter_ask_feedback

## search transactions switch to transfer money, don't continue transactions
* search_transactions OR check_earnings
    - transact_search_form
    - form{"name": "transact_search_form"}
* transfer_money
    - utter_ask_switch_goal
* affirm
    - transfer_form
    - form{"name": "transfer_form"}
    - form{"name": null}
    - utter_ask_back_to_transact
* deny
    - utter_ok
    - utter_ask_feedback

## Transfer money ask account balance
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
* check_balance
    - action_account_balance
    - transfer_form
    - form{"name":null}
    - slot{"requested_slot":null}
    - utter_ask_feedback

## Pay CC ask account balance
* pay_cc
    - cc_payment_form
    - form{"name":"cc_payment_form"}
* check_balance
    - action_account_balance
    - utter_ask_continue
* deny
    - utter_ok
    - form{"name": null}
    - slot{"requested_slot":null}
    - utter_ask_feedback

## Pay CC ask account balance
* pay_cc
    - cc_payment_form
    - form{"name":"cc_payment_form"}
* check_balance
    - action_account_balance
    - utter_ask_continue
* affirm
    - cc_payment_form
    - form{"name": null}
    - slot{"requested_slot":null}
    - utter_ask_feedback

## Transfer money pay credit card
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
* pay_cc
    - cc_payment_form
    - form{"name":"cc_payment_form"}
    - form{"name": null}
    - utter_ask_back_to_transfer
* affirm
    - transfer_form
    - form{"name":"transfer_form"}
    - form{"name": null}
    - utter_ask_feedback

## Transfer money pay credit card
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
* pay_cc
    - cc_payment_form
    - form{"name":"cc_payment_form"}
    - form{"name": null}
    - utter_ask_back_to_transfer
* deny
    - utter_ok
    - utter_ask_feedback

## Show list of known recipients
* check_recipients
    - action_recipients
    - utter_ask_feedback

## Show credit accounts
* check_balance{"account_type":"credit"}
    - action_credit_card_balance
    - utter_ask_feedback

## Show specific credit account
* check_balance{"credit_card":"silver"}
    - action_credit_card_balance
    - utter_ask_feedback

## Show credit accounts
* check_balance{"account_type":"credit","credit_card":"credit card"}
    - action_credit_card_balance
    - utter_ask_feedback

## greet, transfer money, feedback
* greet OR inform{"PERSON": "Stefan"}
    - action_greet_user
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
    - utter_ask_feedback

## transfer money then pay cc
* greet
    - action_greet_user
    - utter_intro
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
* pay_cc
    - cc_payment_form
    - form{"name":"cc_payment_form"}
    - form{"name": null}
    - utter_ask_back_to_transfer
* affirm
    - transfer_form
    - form{"name":"transfer_form"}
    - form{"name": null}
    - utter_ask_feedback

## check recipients, check balance, transfer money
* greet
    - action_greet_user
    - utter_intro
* check_recipients
    - action_recipients
* check_balance{"account_type":"credit"}
    - action_credit_card_balance
    - utter_ask_feedback
* feedback{"feedback_value": "negative"}
    - slot{"feedback_value": "negative"}
    - action_tag_feedback
    - utter_thumbsup
    - utter_anything_else
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
    - utter_ask_feedback

## chitchat --> transfer money --> chitchat
* greet
    - action_greet_user
    - utter_intro
* ask_howdoing
    - utter_howdoing
* whatisPAYbank
    - utter_whatisPAYbank
    - utter_ask_feedback
* feedback{"feedback_value": "positive"}
    - slot{"feedback_value": "positive"}
    - action_tag_feedback
    - utter_great
    - utter_anything_else
* ask_ishuman
    - utter_ishuman
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
    - utter_ask_feedback