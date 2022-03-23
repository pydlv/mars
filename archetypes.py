import json

from util import CrossSection


class Archetype(object):
    feature_type: str
    line: CrossSection
    num_samples: int

    def __init__(self, feature_type: str, line: CrossSection, num_samples: int):
        self.feature_type = feature_type
        self.line = line
        self.num_samples = num_samples


def load_from_file(filename: str) -> dict[str, Archetype]:
    with open(filename, "r") as f:
        data = f.read()

    parsed: dict = json.loads(data)

    results = {}

    for archetype in parsed:
        results[archetype] = Archetype(archetype, parsed[archetype][0], parsed[archetype][1])

    return results
