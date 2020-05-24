## getting positive feedback (method1)
  - utter_ask_feedback
* feedback{"feedback_value": "positive"}
  - slot{"feedback_value": "positive"}
  - utter_great
  - utter_anything_else

## getting positive feedback (method2)
  - utter_ask_feedback
* affirm
  - utter_thumbsup
  - utter_anything_else

## getting negative feedback (method1)
  - utter_ask_feedback
* feedback{"feedback_value": "negative"}
  - slot{"feedback_value": "negative"}
  - utter_ask_feedback_message
  - utter_anything_else

## getting negative feedback (method2)
  - utter_ask_feedback
* deny
  - utter_ask_feedback_message
  - utter_anything_else

## anything else? - yes
  - utter_anything_else
* affirm
  - utter_what_help

## anything else? - no
  - utter_anything_else
* deny
  - utter_thumbsup

## can not help
* canthelp
  - utter_ask_feedback_message

