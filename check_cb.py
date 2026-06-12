import re
import os

callback_regex = re.compile(r'callback_data=["\']([^"\']+)["\']')
handler_regex = re.compile(r'@router\.callback_query\([F\.]*data == ["\']([^"\']+)["\']\)')

defined_callbacks = set()
handled_callbacks = set()

for root, _, files in os.walk("telegram_bot"):
    for file in files:
        if not file.endswith(".py"): continue
        path = os.path.join(root, file)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            for m in callback_regex.findall(content):
                defined_callbacks.add(m)
            for m in handler_regex.findall(content):
                handled_callbacks.add(m)

print("DEFINED but not HANDLED:")
for cb in defined_callbacks - handled_callbacks:
    # Some might be dynamic or prefix based, but let's see
    print(cb)

print("\nHANDLED but not DEFINED:")
for cb in handled_callbacks - defined_callbacks:
    print(cb)

