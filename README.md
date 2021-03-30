# json_logger
python logger that outputs json, helpful for logging to cloudwatch as it will automagically parse json for metrics

allows exceptions to be passed in directly

has two new levels:

  LOG will always log reguardless of the level selected, I wanted to use info for other things.

  SQL wanted to be able to log sql statements at its own level above WARNING but below INFO

has 3 new properties that you can pass in

  sql nice place to get sql statements out, will work on all levels in case you want to log sql for ERROR etc..
  
  custom_dict allows you to pass in a dict that it will expand into json nodes that can be used bu cloudwatch
  
  error allows an exception to be passed in and it will parse it into an error node in the json
  
