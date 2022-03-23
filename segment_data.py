import json
import math
import random
import xml.etree.ElementTree as ET

if __name__ == "__main__":
    tree = ET.parse("all_features.xml")
    root = tree.getroot()

    features = []

    for child in root:
        feature = {
            attribute.tag: attribute.text.strip() for attribute in child
        }
        # There are some features that either have wrong lat/long, or they are wrapping around, so we will just skip those.
        nl = float(feature["northernLatitude"])
        sl = float(feature["southernLatitude"])
        wl = float(feature["westernLongitude"])
        el = float(feature["easternLongitude"])

        if sl < nl and wl < el:
            features.append(feature)
        else:
            print(f"Invalid lat/long for {feature['name']}, skipping.")

    features_by_feature_type = {}

    for feature in features:
        feature_type = feature["featuretype"]
        if feature_type not in features_by_feature_type:
            features_by_feature_type[feature_type] = [feature]
        else:
            features_by_feature_type[feature_type].append(feature)

    testing_features = []
    known_features = []

    for feature_type in features_by_feature_type:
        random.shuffle(features_by_feature_type[feature_type])

        num_features = len(features_by_feature_type[feature_type])

        if num_features < 20:
            # We want at least 20 features to include it in our tests
            continue

        num_testing_features = math.floor(num_features * 0.25)

        num_known_features = num_features - num_testing_features

        for i in range(num_known_features):
            feature = features_by_feature_type[feature_type].pop()
            known_features.append(feature)

        for i in range(num_testing_features):
            feature = features_by_feature_type[feature_type].pop()
            testing_features.append(feature)

    with open("known_features.json", "w") as f:
        f.write(json.dumps(known_features))

    with open("testing_features.json", "w") as f:
        f.write(json.dumps(testing_features))

    print("Num known:", len(known_features))
    print("Num testing:", len(testing_features))

    print("Done.")
