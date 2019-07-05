# Tutorial Knowledge Base

This repository contains the code that is referred to in the tutorial 
[Integrating Rasa with graph databases to encode domain knowledge and resolve entities](TODO).

## Requirements

Install requirements:
```
pip install -r requirements.txt
```

### Setting up the Graph Database

Our knowledge base is represented by a graph database.
In this repository [Grakn](https://grakn.ai/) is used as a graph database.
However, you can also use any other graph database or even write your domain knowledge into a dictionary in the python code directly.

In order to use this code example, you need to install [Grakn](https://grakn.ai/).
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
    graql console --keyspace banking --file knowledge_base/schema.gql
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


## Chat with the Bot

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
- “What is my balance on that account?” 
- “How much money did I spend on food?” 
- “What are my recent transactions?”

## Feedback

If you have any questions about the tutorial or this repository, feel free to share them on [Rasa Community Forum](https://forum.rasa.com/).
