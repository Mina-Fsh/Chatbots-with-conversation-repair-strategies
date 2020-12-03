## faq - whatisPAYbank
* whatisPAYbank
    - utter_whatisPAYbank

## faq - product_description
* product_description
    - utter_product_description

## faq - howtoapply
* howtoapply
    - utter_howtoapply

## faq - application_requirements
* application_requirements
    - utter_application_requirements

## faq - required_age
* required_age
    - utter_required_age

## faq - cardlimit
* cardlimit
    - utter_cardlimit

## faq - points_collect
* points_collect
    - utter_points_collect

## faq - annualcost
* annualcost
    - utter_annualcost

## more faqs
* greet
    - action_greet_user
* whatisPAYbank
    - utter_whatisPAYbank
* product_description
    - utter_product_description

## just check balance
* cardlimit
    - utter_cardlimit
* check_balance
    - action_account_balance

## just transfer money, continue
* greet
    - action_greet_user
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
* points_collect
    - utter_points_collect
    - utter_ask_continue_transfer
* affirm
    - utter_great
    - transfer_form
    - form{"name": null}

## just transfer money, don't continue
* greet
    - action_greet_user
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
* points_collect
    - utter_points_collect
    - utter_ask_continue_transfer
* deny
    - utter_thumbsup
    - action_deactivate_form