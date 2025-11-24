#!/usr/bin/env python3
# Quick script to check what's in the security module

import sys
sys.path.insert(0, '/Users/kolja/Coding/Python/cocobot')

from utils import security
import inspect

print("Classes in security module:")
for name, obj in inspect.getmembers(security):
    if inspect.isclass(obj) and not name.startswith('_'):
        print(f"  - {name}")

print("\nFunctions in security module:")
for name, obj in inspect.getmembers(security):
    if inspect.isfunction(obj) and not name.startswith('_'):
        print(f"  - {name}")

print("\nDone!")