#!/usr/bin/python
# WANT_JSON
#
# Fake package manager module for fast tests. Nothing is installed. The
# requested packages are recorded in a log file on the target, so the
# tests can verify which packages a role would install.

import json
import sys

LOG = "/var/log/ansible-fake-packages.log"

with open(sys.argv[1]) as f:
    args = json.load(f)
names = args.get("name") or args.get("pkg") or []
if isinstance(names, str):
    names = names.split(",")
with open(LOG, "a") as f:
    f.write(json.dumps({"name": names, "state": args.get("state", "present")}) + "\n")
print(json.dumps({"changed": True, "msg": "fake install", "results": names}))
