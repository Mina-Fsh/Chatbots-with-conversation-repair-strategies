## can't help
* canthelp
    - utter_canthelp

## greet + canthelp
* greet
    - action_greet_user
* canthelp
    - utter_canthelp

## greet + cc payment + canthelp + continue
* greet
    - action_greet_user
* pay_cc
    - cc_payment_form
    - form{"name": "cc_payment_form"}
* canthelp
    - utter_canthelp
    - utter_ask_continue_cc_payment
* affirm
    - utter_great
    - cc_payment_form
    - form{"name": null}

## greet + cc payment + canthelp + don't continue
* greet
    - action_greet_user
* pay_cc
    - cc_payment_form
    - form{"name": "cc_payment_form"}
* canthelp
    - utter_canthelp
    - utter_ask_continue_cc_payment
* deny
    - utter_thumbsup
    - action_deactivate_form
    - form{"name": null}

## transfer money + continue
* greet
    - action_greet_user
* transfer_money
    - transfer_form
    - form{"name": "transfer_form"}
* canthelp
    - utter_canthelp
    - utter_ask_continue_transfer
* affirm
    - utter_great
    - transfer_form
    - form{"name": null}

## greet + transfer + canthelp + don't continue
* greet
    - action_greet_user
* transfer_money
    - transfer_form
    - form{"name": "transfer_form"}
* canthelp
    - utter_canthelp
    - utter_ask_continue_transfer
* deny
    - utter_thumbsup
    - action_deactivate_form
    - form{"name": null}
