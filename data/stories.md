## story_greet
* greet
 - utter_greet
 
## story_goodbye
* bye
 - utter_goodbye

## query_entities
* query_entities
- action_query_entities

## request_info
* query_attribute
- action_query_attribute

## resolve entity
* resolve_entity
- action_resolve_entity

## transactions
* greet
  - utter_greet
* query_entities
  - action_query_entities
  - slot{"entity_type": "transactions"}
  - slot{"entities": []}
* compare_entities
  - action_compare_entities
* query_attribute
  - action_query_attribute
  - slot{"transactions": null}
* query_attribute
  - action_query_attribute
* bye
  - utter_goodbye

## transactions
* greet
  - utter_greet
* query_entities
  - action_query_entities
  - slot{"entity_type": "account"}
  - slot{"entities": []}
* query_attribute
  - action_query_attribute
  - slot{"account": null}
* bye
  - utter_goodbye

## transactions
* greet
  - utter_greet
* query_attribute
  - action_query_attribute
  - slot{"bank": null}
* bye
  - utter_goodbye

## transactions
* greet
  - utter_greet
* query_attribute
  - action_query_attribute
* query_entities
  - action_query_entities
* compare_entities
  - action_compare_entities
* bye
  - utter_goodbye
