## chitchat ask builder
* ask_builder
    - utter_builder

## chitchat - ask_howbuilt
* ask_howbuilt
    - utter_howbuild

## chitchat - ask_howdoing 
* ask_howdoing
    - utter_howdoing

## chitchat - ask_howold 
* ask_howold
    - utter_howold

## chitchat - ask_isbot
* ask_isbot
    - utter_isbot

## chitchat - ask_ishuman
* ask_ishuman
    - utter_ishuman

## chitchat - ask_restaurant 
* ask_restaurant 
    - utter_restaurant

## chitchat - ask_time
* ask_time
    - utter_time

## chitchat - ask_languagesbot
* ask_languagesbot
    - utter_languagesbot

## chitchat - ask_weather
* ask_weather
    - utter_weather

## chitchat - ask_whatismyname 
* ask_whatismyname
    - utter_whatismyname

## chitchat - ask_wherefrom
* ask_wherefrom
    - utter_wherefrom

## chitchat - ask_whoami
* ask_whoami
    - utter_whoami

## chitchat - ask_whoisit
* ask_whoisit
    - utter_whoisit

## chitchat - handleinsult
* handleinsult
    - utter_handleinsult

## chitchat - nicetomeetyou
* nicetomeetyou
    - utter_nicetomeetyoutoo

## chitchat - telljoke
* telljoke
    - utter_telljoke

## deny chitchat
* ask_restaurant 
    - utter_isbot
* deny
    - utter_nohelp
    - utter_ask_feedback
* deny
    - utter_thumbsup
    - utter_anything_else

## more chitchat
* greet
    - action_greet_user
* ask_ishuman
    - utter_ishuman
* ask_howold
    - utter_howold
    - utter_ask_feedback
* affirm
    - utter_great
    - utter_anything_else

## just check balance + confirm
* greet
    - action_greet_user
* ask_builder
    - utter_builder
* check_balance
    - action_account_balance
    - utter_ask_feedback
* affirm
    - utter_thumbsup
    - utter_anything_else

## transaction search, continue, + confirm
* greet
    - action_greet_user
* search_transactions OR check_earnings
    - transact_search_form
    - form{"name": "transact_search_form"}
* ask_isbot
    - utter_isbot
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
* search_transactions OR check_earnings
    - transact_search_form
    - form{"name": "transact_search_form"}
* ask_isbot
    - utter_isbot
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
* ask_isbot
    - utter_isbot
* search_transactions OR check_earnings
    - transact_search_form
    - form{"name": "transact_search_form"}
    - form{"name": null}
    - utter_ask_feedback

## just transaction search, continue
* greet
    - action_greet_user
* search_transactions OR check_earnings
    - transact_search_form
    - form{"name": "transact_search_form"}
* ask_howdoing
    - utter_howdoing
    - utter_ask_continue_transact_search
* affirm
    - utter_great
    - transact_search_form
    - form{"name": null}
    - utter_ask_feedback

## just newsletter, don't continue
* greet
    - action_greet_user
* search_transactions OR check_earnings
    - transact_search_form
    - form{"name": "transact_search_form"}
* ask_ishuman
    - utter_ishuman
    - utter_ask_continue_transact_search
* deny
    - utter_thumbsup
    - action_deactivate_form
    - form{"name": null}
    - utter_ask_feedback

## just transfer money
* greet
    - action_greet_user
* ask_isbot
    - utter_isbot
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
    - form{"name": null}
    - utter_ask_feedback

## just transfer money, continue
* greet
    - action_greet_user
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
* ask_ishuman
    - utter_ishuman
    - utter_ask_continue_transfer
* affirm
    - utter_great
    - transfer_form
    - form{"name": null}
    - utter_ask_feedback

## just transfer money, don't continue
* greet
    - action_greet_user
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
* telljoke
    - utter_telljoke
    - utter_ask_continue_transfer
* deny
    - utter_thumbsup
    - action_deactivate_form
    - utter_ask_feedback