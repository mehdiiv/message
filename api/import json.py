import json

# some JSON:
x = '{ "name":"", "age":30, "city":"New York"}'

# parse x:
y = json.loads(x)

# the result is a Python dictionary:
print('%%%%%%%',y["name"])
y["name"] == None
print(y["name"] == '')
