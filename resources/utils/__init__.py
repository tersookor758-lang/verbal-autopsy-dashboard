import json
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RAW_DIR = os.path.join(
    os.path.dirname(BASE_DIR),
    "raw"
)


with open(
    os.path.join(RAW_DIR, "states.json"),
    "r",
    encoding="utf-8"
) as file:

    states = json.load(file)


with open(
    os.path.join(RAW_DIR, "lgas.json"),
    "r",
    encoding="utf-8"
) as file:

    lgas = json.load(file)