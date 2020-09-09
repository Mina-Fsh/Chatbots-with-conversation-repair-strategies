## greet/bye path
* greet
  - action_greet_user
  - utter_intro

## thanks
* thank
    - utter_noworries
    - utter_anything_else

## bye
* bye
    - utter_bye

## greet
* greet OR inform{"PESRON": "akela"}
    - action_greet_user
    - utter_intro

## anything else? - yes
    - utter_anything_else
* affirm
    - utter_what_help

## anything else? - no
    - utter_anything_else
* deny
    - utter_thumbsup

## anything else?
    - utter_anything_else
* inform
    - utter_not_sure
    - utter_intro

## positive reaction
* react_positive
    - utter_react_positive

## negative reaction
* react_negative
    - utter_react_negative

## neither 
* greet
    - action_greet_user
    - utter_intro
* deny
    - utter_nohelp

## pay credit card and check account balance
* pay_cc
    - cc_payment_form
    - form{"name": "cc_payment_form"}
    - form{"name": null}
* check_balance
    - action_account_balance

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

## pay cc happy path no greet
* pay_cc
    - cc_payment_form
    - form{"name": "cc_payment_form"}
    - form{"name": null}
* thank
    - utter_noworries
    - utter_anything_else

## pay credit card happy path
* greet
    - action_greet_user
    - utter_intro
* pay_cc
    - cc_payment_form
    - form{"name": "cc_payment_form"}
    - form{"name": null}

## pay credit card no greet or thanks
* pay_cc
    - cc_payment_form
    - form{"name": "cc_payment_form"}
    - form{"name": null}

## transfer money
* transfer_money
    - transfer_form
    - form{"name": "transfer_form"}
    - form{"name": null}

## is there a transfer charge
* ask_transfer_charge
    - utter_transfer_charge

## transfer money ask transfer charge
* transfer_money
    - transfer_form
    - form{"name": "transfer_form"}
* ask_transfer_charge
    - utter_transfer_charge
    - transfer_form
    - form{"name": "transfer_form"}
    - form{"name": null}
  
## transfer money ask known recipients
* transfer_money
    - transfer_form
    - form{"name": "transfer_form"}
* check_recipients
    - action_recipients
    - transfer_form
    - form{"name": "transfer_form"}
    - form{"name": null}

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
* feedback{"feedback_value": "positive"}
    - slot{"feedback_value": "positive"}
    - action_tag_feedback
    - utter_great
    - utter_anything_else

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

## search transactions happy path
* greet
    - action_greet_user
    - utter_intro
* search_transactions
    - transact_search_form
    - form{"name": "transact_search_form"}
    - form{"name": null}
* thank
    - utter_noworries
    - utter_anything_else

## search transactions happy path no greet
* search_transactions
    - transact_search_form
    - form{"name": "transact_search_form"}
    - form{"name": null}
* thank
    - utter_noworries
    - utter_anything_else

## search transactions happy path no greet or thanks
* search_transactions OR check_earnings
    - transact_search_form
    - form{"name": "transact_search_form"}
    - form{"name": null}

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

## Transfer money ask account balance
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
* check_balance
    - action_account_balance
    - transfer_form
    - form{"name":null}
    - slot{"requested_slot":null}

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

## Show list of known recipients
* check_recipients
    - action_recipients

## Show credit accounts
* check_balance{"account_type":"credit"}
    - action_credit_card_balance

## Show specific credit account
* check_balance{"credit_card":"emblem"}
    - action_credit_card_balance

## Show credit accounts
* check_balance{"account_type":"credit","credit_card":"emblem"}
    - action_credit_card_balance

## greet, transfer money, feedback
* greet OR inform{"PERSON": "Stefan"}
    - action_greet_user
    - utter_intro
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
    - utter_ask_feedback
* feedback{"feedback_value": "positive"}
    - slot{"feedback_value": "positive"}
    - action_tag_feedback
    - utter_great
    - utter_anything_else

## newsletter then sales
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
* feedback{"feedback_value": "positive"}
    - slot{"feedback_value": "positive"}
    - action_tag_feedback
    - utter_great
    - utter_anything_else

## newsletter, confirm, then sales
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
* feedback{"feedback_value": "positive"}
    - slot{"feedback_value": "positive"}
    - action_tag_feedback
    - utter_great
    - utter_anything_else

## chitchat --> transfer money --> no email
* greet
    - action_greet_user
    - utter_intro
* chitchat
    - respond_chitchat
* chitchat
    - respond_chitchat
* chitchat
    - respond_chitchat
* chitchat
    - respond_chitchat
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
    - utter_ask_feedback
* feedback{"feedback_value": "negative"}
    - slot{"feedback_value": "negative"}
    - action_tag_feedback
    - utter_thumbsup
    - utter_anything_else
    









