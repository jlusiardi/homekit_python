import json


def load_pairing(file: str) -> dict:
    """
    loads data for an existing pairing from the file.

    :param file: the file name
    :return: a dict containing the pairing data or None if file was not found
    """
    try:
        with open(file, 'r') as input_fp:
            return json.load(input_fp)
    except FileNotFoundError:
        return None


def save_pairing(file: str, pairing_data: dict):
    """
    save the data for an existing pairing.

    :param file: the file name
    :param pairing_data: a dict containing the pairing data
    :return: None
    """
    with open(file, 'w') as output_fp:
        json.dump(pairing_data, output_fp, indent=4)
