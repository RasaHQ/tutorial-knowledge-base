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
  - slot{"mention": null}
  - slot{"bank": "N26"}

## resolve entity
* resolve_entity
  - action_resolve_entity
  - slot{"mention": null}
  - slot{"bank": "N26"}

## transactions
* greet
  - utter_greet
* query_entities
  - action_query_entities
  - slot{"entity_type": "transaction"}
  - slot{"entities": []}
  - slot{"transaction": ""}
* compare_entities
  - action_compare_entities
* query_attribute
  - action_query_attribute
  - slot{"mention": null}
  - slot{"account": "DE89370400440532013000"}
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
  - slot{"account": ""}
* query_attribute
  - action_query_attribute
  - slot{"mention": null}
  - slot{"transaction": "123"}
* bye
  - utter_goodbye

## transactions
* greet
  - utter_greet
* query_attribute
  - action_query_attribute
  - slot{"mention": null}
  - slot{"card": null}
* bye
  - utter_goodbye

## transactions
* greet
  - utter_greet
* query_attribute
  - action_query_attribute
  - slot{"mention": null}
  - slot{"person": null}
* query_entities
  - action_query_entities
* compare_entities
  - action_compare_entities
* bye
  - utter_goodbye
