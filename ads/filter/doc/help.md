# What is filters.json?

This file contains all the filters that are used in the program.  
The filters are used to filter out logs of a certain type and
create a new source with property values as a name for new soruce.

## Example of basic source and with fileter

*Basic Source:*

```bash
"name-gov.sk"
```

*Source with filters "process.name", "process.id":*

```bash
"name-gov.sk->somename->1829"
"name-gov.sk->somename->1322"
"name-gov.sk->differentname->1829"
...
```

## Example of filters.json

```json
{
    "name-gov.sk": {
        "property": ["process.name", "process.id"]
    },
    ...
}
```

```json
{
    "slot1/ba4-gov-lb.mgmt.gov.sk": {
        "property": ["process.name", "process.id"]
    }
}
```

## Example of empty filters.json

```json
{}
```

## Properties and their meanings

- **some-name**: The name of the filter. This is used to identify the filter.  
For example - `192.168.0.80` or `smth.gov.sk`

- **property**: The properties that are used to filter out logs.
Can be multiple properties. That are part of log structure.