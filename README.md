# Tutorial Knowledge Base

This repository contains the code that is referred to in the tutorial 
[Integrating Rasa with knowledge bases](https://blog.rasa.com/integrating-rasa-with-knowledge-bases/).


**UPDATE**: 
We added [Knowledge Base Actions](https://rasa.com/docs/rasa/core/knowledge-bases/) to Rasa.
[Knowledge Base Actions](https://rasa.com/docs/rasa/core/knowledge-bases/) help you to connect your knowledge base to Rasa more quickly.
Try it out and share your feedback on the [Rasa Community Forum](https://forum.rasa.com/).


## Outline

1. [Requirements](#Requirements)
   * [Setting up the Graph Database](#Setting-up-the-Graph-Database)
   * [Alternative to Graph Databases](#Alternative-to-Graph-Databases)
2. [Chat with the Bot](#Chat-with-the-Bot)
3. [Limitations of Knowledge Bases](#Limitations-of-Knowledge-Bases)
4. [Feedback](#Feedback)


## Requirements

Install requirements:
```
pip install -r requirements.txt
```

### Setting up the Graph Database

Our knowledge base is represented by a graph database.
In this repository [Grakn](https://grakn.ai/) is used as a graph database.
However, you can also use any other graph database or use an alternative (see below).

In order to use this code example, you need to install [Grakn](https://grakn.ai/).
To be able to run this bot, you need version 1.5.7.
Please check the [installation instruction](https://dev.grakn.ai/docs/running-grakn/install-and-run)
of Grakn in order to install it.
Once you installed Grakn, you need to start the Grakn server by executing
```bash
grakn server start
```
You can stop the server by running `grakn server stop`.

In order to get some data into the graph database you need to execute the following steps:
1. Create the schema by executing
    ```bash
    grakn console --keyspace banking --file <absolute-path-to-knowledge_base/schema.gql>
    ```
    This will create a keyspace `banking` in your Grakn graph database with the schema defined in `knowledge_base/schema.gql`.
2. Load data into your schema by running 
    ```bash
    python knowledge_base/migrate.py
    ```
    Grakn recommends you to write a `migrate.py` script 
    (see [migration-python](https://dev.grakn.ai/docs/examples/phone-calls-migration-python))
    to load data from csv files into your graph database.
    Our migration script loads the data located in `knowledge_base/data` into the keyspace `banking`.

The graph database is set up and ready to be used.

### Alternative to Graph Databases

If you just have a small knowledge base and you don't want to install and set up a graph database, such as Grakn,
you can also encode your domain knowledge in a data structure, such as a python dictionary.
You can find an example in the file `graph_database.py`.
The file contains an implementation that uses a graph database (class `GraphDatabase`) and an implementation
that simply uses a python dictionary as domain knowledge (class `InMemoryGraph`).
If you want to use the `InMemoryGraph` instead of the `GraphDatabase` in the bot, you need to exchange the
initialization of the graph database in `actions.py`.
But be aware of the fact, that the `InMemoryGraph` does not cover the same knowledge as the `GraphDatabase`.
It just knows about banks and their attributes.


## Chat with the Bot

Make sure you installed all requirements and your grakn server is running.

If you want to chat with the bot, execute the following steps:
1. Train the bot using `rasa train`.
2. Start the action server with `rasa run actions` in a separate terminal.
3. Chat with the bot on the command line by executing `rasa shell`.

If you want to see what slots are set and how confident the bot is in predicting the next action, you should run 
the bot in debug mode: `rasa shell --debug`.

Here are some example questions you can ask the bot:
- “What are my bank options?”
- “What is the headquarter of the first bank?”
- “What accounts do I have?” 
- “What is my balance on the second account?” 
- “What are my recent transactions?”


## Limitations of Knowledge Bases

Before we look at the limitations of knowledge bases, let's first take a look, in what way an entity can be referenced:

| Type                            | Example                                                                                               | Description                                                                                                                                                                        |
|---------------------------------|-------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| direct mention                  | _Rasa_ is located in _Berlin_.                                                                        | An entity was mentioned by its name in the text, such as _Rasa_ or _Berlin_.                                                                                                       |
| ordinal mention                 | Where is the headquarters of the _third_ company?                                                     | The user was confronted to a list of entities. The user refers to an entity of that list by its position.                                                                          |
| mention by synonym              | What's my _balance_? vs. How much _cash_ do I have?                                                   | The user refers to the same entity with different names.                                                                                                                           |                                                                              
| ambiguous mention               | I want to transfer money to _John_?                                                                   | The bot can find multiple entities with the referenced name (e.g. _John_). The entity needs to be specified.                                                                       |                                                           
| mention by pronoun              | _Rasa_ is located in _Berlin_. _It_ is an open source company.                                                                       | Reference to a previous mentioned entity by its pronoun, such as _it_.                                                                                                             |   
| mention by hypernyms & hyponyms | Here are some recent transactions: Raynair 99.95€, Spotify 9.99€. Which do you want to dispute?       | The user can answer many things, such as "the subscription", or "the plane ticket". The bot needs to understand what entity the user refers to by those answers.                   |                                                                                 
| mention by attribute(s)         | Where is the headquarters of the _open source_ company that _builds chatbots_?                        | Find an entity in the knowledge base that fits the mentioned criteria.                                                                                                             |  
| mention by attribute comparison | Your last transactions: Amazon 99.95€, Netflix 4.99€. Which do you want to dispute?                   | If the user says, for example, "the bigger one", the bot needs to first resolve the comparison before he can detect the entity the user is referring to.                           |                                                                                 


The bot in this repo can handle some but not all of  the cases above.
Let's go over them one by one and take a closer look at what is possible and what are current limitations:

**direct mention**

The direct mention is handled by the NER of Rasa.
No knowledge base is needed to recognize an entity in a text.
However, your knowledge base can be used to create [lookup tables](https://rasa.com/docs/rasa/nlu/training-data-format/#lookup-tables), that can then be used to improve the NER.

**mention by pronoun**

If an entity is referred to by its pronoun, the bot cannot detect it.
Let's look at the example "My sister has a dog. She loves him."
In the example "him" is referring to "dog" and "she" refers to "sister".
However, for the bot it is hard to figure that out.
Typically, coreference resolution models are used to solve this kind of mention.
Here are some links to repositories:
* [huggingface](https://github.com/huggingface/neuralcoref)
* [allennlp](https://demo.allennlp.org/coreference-resolution/OTM5MjM3)
* [standford nlp](https://nlp.stanford.edu/projects/coref.shtml)

**ordinal mention**

With the smart use of slots, your bot is able to resolve an ordinal mention to its real-world entity (see [code snippet](https://github.com/RasaHQ/tutorial-knowledge-base/blob/master/actions.py#L11)).
As soon as multiple entities from the knowledge base are listed, the bot stores those in a specific slot (`listed_items`).
The recognized ordinal mention needs to be mapped to an index and the entity can be picked up from the list of entities using the identified index.

**mention by attribute(s)**

Theoretically, your bot can find any entity by its attributes in its knowledge base.
However, if you requested, for example, to name the transaction you did last month to Max, multiple nodes and
relations in your graph database are involved.
The query to fetch the requested entity becomes quite complex.
The bot is currently not able to handle such complex requests.
But, if you simply ask for a specific entity that just involves a node and its attributes in the graph database,
the bot can answer your request.

**ambiguous mention**

Your bot should be able to help you resolve an ambiguous mention.
For example, if you want to transfer money to John, but you have transferred money to John Doe and John Mustermann in the past,
the bot needs you to confirm which exact John you meant.
In order to archive that, the bot looks up the ambiguous entity in the knowledge base.
If multiple entities are found, you will be confronted with the list of entities.
You can then specify the entity you meant by, for example, using an ordinal mention.

**mention by synonym**

The bot uses mapping tables in the knowledge base to resolve synonyms, e.g. mapping `cash` and `balance` to the same entity. 
However, this is limited to the names you defined in those mapping tables.

**mention by hypernyms & hyponyms**

The bot cannot handle mentions by hypernyms & hyponyms at the moment.
Knowledge about, for example, Rynair selling plane tickets is missing.
If such knowledge can be encoded in your knowledge base, more complex queries could be used to retrieve the information of interest.

**mention by attribute comparison**

If you say something like "Please, dispute the biggest of the just listed transactions.", the bot first needs to 
compare multiple entities by certain attributes before it can pick the entity of interest.
As the bot currently cannot perform a comparison, this kind of mention cannot be handled by the bot at the moment.


Apart from the limitation already listed per mention type, the bot has some further limitations:
* _Comparing entities is still limited_: 
The bot is not able to detect the comparison operator and can therefore not compare multiple entities in a proper way. 
For example, if the bot listed your accounts and you are asking "On what account do I currently have more money?".
The bot needs to recognize not only that you are interested in the balance of the listed accounts, but also that 
"more money" means that the accounts need to be compared by their balance and you only want to know
about the account with the highest balance.
So far, the bot just lists the requested attribute for all entities and you have to "compare" yourself.

* _Executing complex queries_: 
The bot tries to handle requests in a generic way. 
However, some user requests, such as "How much money did I transfer to Max from my N26 account in the last month.", require complex queries. 
The example request involves the nodes "person", "bank", and "account" as well as the relations "transaction" and "contract".
As those requests are very specific and the resulting query is complex, the bot needs to handle them separately.
However, this special treatment is currently not implemented, so that the bot is not able to answer complex queries that involve multiple nodes and relations.

## Feedback

If you have any questions about the tutorial or this repository, feel free to share them on [Rasa Community Forum](https://forum.rasa.com/).
