## Configuration parameters
This extractor refers to **Skills** as **Workspaces** as this is how they are referred to in the documentation of the API.
  
- **#api_key**:
    Your IBM Watson Assistant api key
- **mode** :
  either 'list_all_logs' or 'workspace'. If 'list_all_logs' is set then the parameter list_logs_filter must be set. If 'workspace' is set then workspace_id must be set

- **list_logs_filter**:
        Filter for list all logs, docs of filter can be found [here](https://cloud.ibm.com/docs/assistant?topic=assistant-filter-reference#filter-reference). You must specify a filter query that includes a value for language, as well as a value for request.context.system.assistant_id, workspace_id, or request.context.metadata.deployment.
- **workspace_id**:
    Id of the skill/workspace that you wish to write data to 
  
- **version**:
    version of the API you wish to use e.g. 2019-02-28
  

## Sample Configuration
```json
{
    "workspace_id": "ID_OF_WORKSPACE_HERE",
    "#api_key": "API_KEY_HERE",
    "version": "2019-02-28"
}
```
Or
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