# -*- coding: utf-8 -*-
from typing import Text, Dict, Any, List, Union

from rasa_sdk.events import SlotSet
from rasa_sdk import Action, Tracker

from schema import schema
from graph_database import GraphDatabase


def resolve_mention(tracker: Tracker) -> Text:
    """
    Resolves a mention of an entity, such as first, to the actual entity.
    If multiple entities are listed during the conversation, the entities
    are stored in the slot 'listed_items' as a list. We resolve the mention,
    such as first, to the list index and retrieve the actual entity.

    :param tracker: tracker
    :return: name of the actually entity
    """
    graph_database = GraphDatabase()

    mention = tracker.get_slot("mention")
    listed_items = tracker.get_slot("listed_items")

    if mention is not None and listed_items is not None:
        idx = int(graph_database.map("mention-mapping", mention))

        if type(idx) is int and idx < len(listed_items):
            return listed_items[idx]


def get_entity_type(tracker: Tracker) -> Text:
    """
    Get the entity type mentioned by the user. As the user may speak of an
    entity type in plural, we need to map the mentioned entity type to the
    type used in the knowledge base.

    :param tracker: tracker
    :return: entity type (same type as used in the knowledge base)
    """
    graph_database = GraphDatabase()
    entity_type = tracker.get_slot("entity_type")
    return graph_database.map("entity-type-mapping", entity_type)


def get_attribute(tracker: Tracker) -> Text:
    """
    Get the attribute mentioned by the user. As the user may use a synonym for
    an attribute, we need to map the mentioned attribute to the
    attribute name used in the knowledge base.

    :param tracker: tracker
    :return: attribute (same type as used in the knowledge base)
    """
    graph_database = GraphDatabase()
    attribute = tracker.get_slot("attribute")
    return graph_database.map("attribute-mapping", attribute)


def get_entity_name(tracker: Tracker, entity_type: Text):
    """
    Get the name of the entity the user referred to. Either the NER detected the
    entity and stored its name in the corresponding slot or the user referred to
    the entity by an ordinal number, such as first or last, or the user refers to
    an entity by its attributes.

    :param tracker: Tracker
    :param entity_type: the entity type

    :return: the name of the actual entity (value of key attribute in the knowledge base)
    """

    # user referred to an entity by an ordinal number
    mention = tracker.get_slot("mention")
    if mention is not None:
        return resolve_mention(tracker)

    # user named the entity
    entity_name = tracker.get_slot(entity_type)
    if entity_name:
        return entity_name

    # user referred to an entity by its attributes
    listed_items = tracker.get_slot("listed_items")
    attributes = get_attributes_of_entity(entity_type, tracker)

    if listed_items and attributes:
        # filter the listed_items by the set attributes
        graph_database = GraphDatabase()
        for entity in listed_items:
            key_attr = schema[entity_type]["key"]
            result = graph_database.validate_entity(
                entity_type, entity, key_attr, attributes
            )
            if result is not None:
                return to_str(result, key_attr)

    return None


def get_attributes_of_entity(entity_type, tracker):
    # check what attributes the NER found for entity type
    attributes = []
    if entity_type in schema:
        for attr in schema[entity_type]["attributes"]:
            attr_val = tracker.get_slot(attr.replace("-", "_"))
            if attr_val is not None:
                attributes.append({"key": attr, "value": attr_val})
    return attributes


def reset_attribute_slots(slots, entity_type, tracker):
    # check what attributes the NER found for entity type
    if entity_type in schema:
        for attr in schema[entity_type]["attributes"]:
            attr = attr.replace("-", "_")
            attr_val = tracker.get_slot(attr)
            if attr_val is not None:
                slots.append(SlotSet(attr, None))
    return slots


def to_str(entity: Dict[Text, Any], entity_keys: Union[Text, List[Text]]) -> Text:
    """
    Converts an entity to a string by concatenating the values of the provided
    entity keys.

    :param entity: the entity with all its attributes
    :param entity_keys: the name of the key attributes
    :return: a string that represents the entity
    """
    if isinstance(entity_keys, str):
        entity_keys = [entity_keys]

    v_list = []
    for key in entity_keys:
        _e = entity
        for k in key.split("."):
            _e = _e[k]

        if "balance" in key or "amount" in key:
            v_list.append(f"{str(_e)} €")
        elif "date" in key:
            v_list.append(_e.strftime("%d.%m.%Y (%H:%M:%S)"))
        else:
            v_list.append(str(_e))
    return ", ".join(v_list)


class ActionQueryEntities(Action):
    """Action for listing entities.
    The entities might be filtered by specific attributes."""

    def name(self):
        return "action_query_entities"

    def run(self, dispatcher, tracker, domain):
        graph_database = GraphDatabase()

        # first need to know the entity type we are looking for
        entity_type = get_entity_type(tracker)

        if entity_type is None:
            dispatcher.utter_template("utter_rephrase", tracker)
            return []

        # check what attributes the NER found for entity type
        attributes = get_attributes_of_entity(entity_type, tracker)

        # query knowledge base
        entities = graph_database.get_entities(entity_type, attributes)

        # filter out transactions that do not belong the set account (if any)
        if entity_type == "transaction":
            account_number = tracker.get_slot("account")
            entities = self._filter_transaction_entities(entities, account_number)

        if not entities:
            dispatcher.utter_template(
                "I could not find any entities for '{}'.".format(entity_type), tracker
            )
            return []

        # utter a response that contains all found entities
        # use the 'representation' attributes to print an entity
        entity_representation = schema[entity_type]["representation"]

        dispatcher.utter_message(
            "Found the following '{}' entities:".format(entity_type)
        )
        sorted_entities = sorted([to_str(e, entity_representation) for e in entities])
        for i, e in enumerate(sorted_entities):
            dispatcher.utter_message(f"{i + 1}: {e}")

        # set slots
        # set the entities slot in order to resolve references to one of the found
        # entites later on
        entity_key = schema[entity_type]["key"]

        slots = [
            SlotSet("entity_type", entity_type),
            SlotSet("listed_items", list(map(lambda x: to_str(x, entity_key), entities))),
        ]

        # if only one entity was found, that the slot of that entity type to the
        # found entity
        if len(entities) == 1:
            slots.append(SlotSet(entity_type, to_str(entities[0], entity_key)))

        reset_attribute_slots(slots, entity_type, tracker)

        return slots

    def _filter_transaction_entities(
        self, entities: List[Dict[Text, Any]], account_number: Text
    ) -> List[Dict[Text, Any]]:
        """
        Filter out all transactions that do not belong to the provided account number.

        :param entities: list of transactions
        :param account_number: account number
        :return: list of filtered transactions with max. 5 entries
        """
        if account_number is not None:
            filtered_entities = []
            for entity in entities:
                if entity["account-of-creator"]["account-number"] == account_number:
                    filtered_entities.append(entity)
            return filtered_entities[:5]

        return entities[:5]


class ActionQueryAttribute(Action):
    """Action for querying a specific attribute of an entity."""

    def name(self):
        return "action_query_attribute"

    def run(self, dispatcher, tracker, domain):
        graph_database = GraphDatabase()

        # get entity type of entity
        entity_type = get_entity_type(tracker)

        if entity_type is None:
            dispatcher.utter_template("utter_rephrase", tracker)
            return []

        # get name of entity and attribute of interest
        name = get_entity_name(tracker, entity_type)
        attribute = get_attribute(tracker)

        if name is None or attribute is None:
            dispatcher.utter_template("utter_rephrase", tracker)
            slots = [SlotSet("mention", None)]
            reset_attribute_slots(slots, entity_type, tracker)
            return slots

        # query knowledge base
        key_attribute = schema[entity_type]["key"]
        value = graph_database.get_attribute_of(
            entity_type, key_attribute, name, attribute
        )

        # utter response
        if value is not None and len(value) == 1:
            dispatcher.utter_message(
                f"{name} has the value '{value[0]}' for attribute '{attribute}'."
            )
        else:
            dispatcher.utter_message(
                f"Did not found a valid value for attribute {attribute} for entity '{name}'."
            )

        slots = [SlotSet("mention", None), SlotSet(entity_type, name)]
        reset_attribute_slots(slots, entity_type, tracker)
        return slots


class ActionCompareEntities(Action):
    """Action for comparing multiple entities."""

    def name(self):
        return "action_compare_entities"

    def run(self, dispatcher, tracker, domain):
        graph = GraphDatabase()

        # get entities to compare and their entity type
        listed_items = tracker.get_slot("listed_items")
        entity_type = get_entity_type(tracker)

        if listed_items is None or entity_type is None:
            dispatcher.utter_template("utter_rephrase", tracker)
            return []

        # get attribute of interest
        attribute = get_attribute(tracker)

        if attribute is None:
            dispatcher.utter_template("utter_rephrase", tracker)
            return []

        # utter response for every entity that shows the value of the attribute
        for e in listed_items:
            key_attribute = schema[entity_type]["key"]
            value = graph.get_attribute_of(entity_type, key_attribute, e, attribute)

            if value is not None and len(value) == 1:
                dispatcher.utter_message(
                    f"{e} has the value '{value[0]}' for attribute '{attribute}'."
                )

        return []


class ActionResolveEntity(Action):
    """Action for resolving a mention."""

    def name(self):
        return "action_resolve_entity"

    def run(self, dispatcher, tracker, domain):
        entity_type = tracker.get_slot("entity_type")
        listed_items = tracker.get_slot("listed_items")

        if entity_type is None:
            dispatcher.utter_template("utter_rephrase", tracker)
            return []

        # Check if entity was mentioned as 'first', 'second', etc.
        mention = tracker.get_slot("mention")
        if mention is not None:
            value = resolve_mention(tracker)
            if value is not None:
                return [SlotSet(entity_type, value), SlotSet("mention", None)]

        # Check if NER recognized entity directly
        # (e.g. bank name was mentioned and recognized as 'bank')
        value = tracker.get_slot(entity_type)
        if value is not None and value in listed_items:
            return [SlotSet(entity_type, value), SlotSet("mention", None)]

        dispatcher.utter_template("utter_rephrase", tracker)
        return [SlotSet(entity_type, None), SlotSet("mention", None)]
