## ordering a gearbox happy path
* order_gearbox
    - order_gearbox_form
    - form{"name":"order_gearbox_form"}
    - slot{"requested_slot":"num_gears"}
* inform{"num_gears":"2"}
    - slot{"num_gears":"2"}
    - utter_ask_gear_one_size
* inform{"gear_one_size":"mittel"}
    - slot{"gear_one_size":"mittel"}
    - utter_ask_gear_two_size
* inform{"gear_two_size":"klein"}
    - slot{"gear_two_size":"klein"}
    - utter_ask_gear_one_polishing
* inform{"gear_one_polishing":"ja"}
    - slot{"gear_one_polishing":"ja"}
    - utter_ask_gear_two_polishing
    - utter_submit


## ordering a gearbox stop
* order_gearbox
  - order_gearbox_form
  - form{"name": "order_gearbox_form"}
* out_of_scope
  - utter_ask_continue
* deny
  - action_deactivate_form
  - form{"name": null}

## ordering a gearbox continue
* order_gearbox
  - order_gearbox_form
  - form{"name": "order_gearbox_form"}
* stop
  - utter_ask_continue
* affirm
  - order_gearbox_form
  - form{"name": null}
