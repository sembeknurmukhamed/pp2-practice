import json

# open() reads the file, json.load() converts the JSON text
# into a Python dictionary (dict) so we can work with it normally.

with open(r"c:\Users\tacoc\OneDrive\Рабочий стол\pp_2\practice-4\exercises\work-with-json\sample-data.json") as f:
    data = json.load(f)

# At this point, `data` is just a regular Python dict.
# You can verify this:
# print(type(data))   →  <class 'dict'>


# The top level has two keys: "totalCount" and "imdata"
# "imdata" is a LIST of interfaces, where each item looks like:
#
#   {
#     "l1PhysIf": {
#       "attributes": {
#         "dn":    "topology/pod-1/node-201/sys/phys-[eth1/33]",
#         "descr": "",
#         "speed": "inherit",
#         "mtu":   "9150"
#       }
#     }
#   }
#
# So the path to get the "dn" of the first interface is:
#   data["imdata"][0]["l1PhysIf"]["attributes"]["dn"]


print("Interface Status")
print("=" * 80)
# f-strings let us pad/align text inside columns using format specs:
#   {value:<50}  →  left-align in a 50-character wide column
#   {value:>6}   →  right-align in a 6-character wide column
print(f"{'DN':<50} {'Description':<12} {'Speed':>6}   {'MTU':>6}")
print(f"{'-'*50} {'-'*12}  {'-'*7}    {'-'*4}")


for item in data["imdata"]:

    attrs = item["l1PhysIf"]["attributes"]

    dn    = attrs["dn"]
    descr = attrs["descr"]   # empty string ""
    speed = attrs["speed"]
    mtu   = attrs["mtu"]

    print(f"{dn:<50} {descr:<12}  {speed:>6}  {mtu:>6}")
