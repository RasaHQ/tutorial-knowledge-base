## greet
* greet
  - utter_greet
 
## goodbye
* bye
  - utter_goodbye

## query entities
* query_entities
  - action_query_entities
  - slot{"category": null}

## query attribute
* query_attribute
  - action_query_attribute
  - slot{"mention": null}
  - slot{"bank": "N26"}

## resolve entity
* resolve_entity
  - action_resolve_entity
  - slot{"mention": null}
  - slot{"bank": "N26"}
  - slot{"account": "DE76894768662419673111"}
  
## out of scope
* out_of_scope
  - utter_out_of_scope
  
## help
* help
  - utter_help

## conversation #1
* greet
  - utter_greet
* query_entities
  - action_query_entities
  - slot{"entity_type": "transaction"}
  - slot{"listed_items": []}
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

## conversation #2
* greet
  - utter_greet
* query_entities
  - action_query_entities
  - slot{"entity_type": "account"}
  - slot{"listed_items": []}
  - slot{"account": ""}
* query_attribute
  - action_query_attribute
  - slot{"mention": null}
  - slot{"transaction": "123"}
* bye
  - utter_goodbye

## conversation #3
* greet
  - utter_greet
* query_attribute
  - action_query_attribute
  - slot{"mention": null}
  - slot{"card": null}
* bye
  - utter_goodbye

## conversation #4
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

## conversation #5
* greet
  - utter_greet
* query_entities
  - action_query_entities
  - slot{"entity_type": "transaction"}
  - slot{"listed_items": []}
  - slot{"transaction": ""}
* out_of_scope
  - utter_out_of_scope
* query_attribute
  - action_query_attribute
  - slot{"mention": null}
  - slot{"account": "DE89370400440532013000"}
* bye
  - utter_goodbye

## conversation #6
* greet
  - utter_greet
* out_of_scope
  - utter_out_of_scope
* query_attribute
  - action_query_attribute
  - slot{"mention": null}
  - slot{"person": null}
* query_entities
  - action_query_entities
* compare_entities
  - action_compare_entities
* out_of_scope
  - utter_out_of_scope
* bye
  - utter_goodbye

## conversation #7
* greet
  - utter_greet
* query_entities
  - action_query_entities
  - slot{"entity_type": "account"}
  - slot{"listed_items": []}
  - slot{"account": ""}
* query_attribute
  - action_query_attribute
  - slot{"mention": null}
  - slot{"transaction": "123"}
* out_of_scope
  - utter_out_of_scope
* bye
  - utter_goodbye

## conversation #8
* greet
  - utter_greet
* query_entities
  - action_query_entities
  - slot{"entity_type": "transaction"}
  - slot{"listed_items": []}
  - slot{"transaction": ""}
* out_of_scope
  - utter_out_of_scope
* help
  - utter_help
* query_attribute
  - action_query_attribute
  - slot{"mention": null}
  - slot{"account": "DE89370400440532013000"}
* query_attribute
  - action_query_attribute
* bye
  - utter_goodbye

## conversation #9
* greet
  - utter_greet
* out_of_scope
  - utter_out_of_scope
* help
  - utter_help
* query_entities
  - action_query_entities
  - slot{"entity_type": "transaction"}
  - slot{"listed_items": []}
  - slot{"transaction": ""}
* query_attribute
  - action_query_attribute
  - slot{"mention": null}
  - slot{"account": "DE89370400440532013000"}
* bye
  - utter_goodbye