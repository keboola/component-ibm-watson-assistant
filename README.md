IBM Watson Assistant Extracor
=============

IBM Watson Assistant is a cloud service that allows developers to embed an artificial intelligence virtual assistant in
the software they are developing and brand the assistant as their own.

This extractor enables users extract the settings of specified skills. The setting data of a skill contain intents,
entities, and dialogs.

For more information on skills, entities, intents, and dialogs see the IBM watson documentation.

**Table of contents:**

[TOC]

Functionality notes
===================
This extractor refers to **Skills** as **Workspaces** as this is how they are referred to in the documentation of the API.

The extractor uses the ibm_watson python sdk utilizing the get_workspace() to download the whole workspace settings.

Prerequisites
=============

Get the API token of IBM Watson assistant

Configuration
=============

mode
-------
either 'list_all_logs' or 'workspace'. If 'list_all_logs' is set then the parameter list_logs_filter must be set. If 'workspace' is set then workspace_id must be set

list_logs_filter
-------
Filter for list all logs, docs of filter can be found [here](https://cloud.ibm.com/docs/assistant?topic=assistant-filter-reference#filter-reference). You must specify a filter query that includes a value for language, as well as a value for request.context.system.assistant_id, workspace_id, or request.context.metadata.deployment.

workspace_id
-------
Id of the skill/workspace that you wish to write data to 

#api_key
-------
You IBM Watson Assistant api key

version
-------
version of the API you wish to use


Sample Configuration
=============
```json
{
  "parameters": {
    "workspace_id": "ID_OF_WORKSPACE_HERE",
    "#api_key": "API_KEY_HERE",
    "version": "2019-02-28"
  }
}
```
```json
{
  "parameters": {
    "#api_key": "API_KEY_HERE",
    "version": "2019-02-28",
    "mode" : "list_all_logs",
    "list_logs_filter" : "language::en,workspace_id::ID_OF_WORKSPACE_HERE"
  }
}
```
Output
======

JSON file containing the settings of the workspace.

Example of output:

```json
{
  "status": "Available",
  "name": "Test_Keboola",
  "intents": [
    {
      "intent": "test_intent",
      "examples": [
        {
          "text": "test"
        }
      ]
    }
  ],
  "entities": [
    {
      "entity": "test",
      "values": [
        {
          "type": "synonyms",
          "value": "val",
          "synonyms": [
            "syn"
          ]
        },
        {
          "type": "synonyms",
          "value": "test",
          "synonyms": [
            "syns"
          ]
        }
      ],
      "fuzzy_match": false
    }
  ],
  "language": "cs",
  "metadata": {
    "skill": {
      "counts": {
        "intents": 1,
        "entities": 1,
        "dialog_nodes": 1
      }
    },
    "api_version": {
      "major_version": "v1",
      "minor_version": "2019-02-28"
    }
  },
  "webhooks": [
    {
      "url": "",
      "name": "main_webhook",
      "headers": []
    }
  ],
  "description": "Test Keboola",
  "dialog_nodes": [
    {
      "type": "standard",
      "title": "test",
      "output": {
        "generic": [
          {
            "values": [
              {
                "text": "test text"
              }
            ],
            "response_type": "text",
            "selection_policy": "random"
          }
        ]
      },
      "parent": "node_id",
      "next_step": {
        "behavior": "jump_to",
        "selector": "body",
        "dialog_node": "node_id"
      },
      "conditions": "#test",
      "dialog_node": "node_id",
      "previous_sibling": "node_id",
      "disambiguation_opt_out": true
    }
  ],
  "workspace_id": "workspace id",
  "counterexamples": [
    {
      "text": "counter"
    }
  ],
  "system_settings": {
    "tooling": {
      "store_generic_responses": true
    },
    "disambiguation": {
      "prompt": "promot test",
      "enabled": false,
      "randomize": true,
      "max_suggestions": 3,
      "suggestion_text_policy": "user_label",
      "none_of_the_above_prompt": ""
    },
    "system_entities": {
      "enabled": true
    }
  },
  "learning_opt_out": false
}
```

Use Case 
=============
This extractor is set to be used with the writer component.

You can set up an orchestration of extract > transform > write. 
Add the output json as input of the transformation, and the input of the writer as the output of the transformation.

A sample transformation:

```
import json
from keboola.component.interface import CommonInterface

ci = CommonInterface()

input_file = ci.get_input_files_definitions(only_latest_files=True)[0]

with open(input_file.full_path, "r") as input_file:
	workspace_data = json.load(input_file)
  
for i,intent in enumerate(workspace_data["intents"]):
  workspace_data["intents"][i]["intent"] = f"{intent['intent']}_UPDATED"
  
with open("out/files/updated_WORKSPACE_ID_workspace.json", "w") as output_file:
	workspace_data = json.dump(workspace_data, output_file)
```

Development
-----------

If required, change local data folder (the `CUSTOM_FOLDER` placeholder) path to
your custom path in the `docker-compose.yml` file:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    volumes:
      - ./:/code
      - ./CUSTOM_FOLDER:/data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Clone this repository, init the workspace and run the component with following
command:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
git clone https://bitbucket.org/kds_consulting_team/kds-team.ex-ibm-watson-assistant/src/master/ kds-team.ex-ibm-watson-assistant
cd kds-team.ex-ibm-watson-assistant
docker-compose build
docker-compose run --rm dev
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the test suite and lint check using this command:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
docker-compose run --rm test
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Integration
===========

For information about deployment and integration with KBC, please refer to the
[deployment section of developers
documentation](https://developers.keboola.com/extend/component/deployment/)
