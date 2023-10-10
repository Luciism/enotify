"""A bunch of random useful functions"""

import json
import os

from .common import PROJECT_PATH


_config_data: dict = None


def resolve_config_file() -> str:
    file_path = os.getenv('config_file')
    return file_path.format(PROJECT_PATH=PROJECT_PATH)


def load_config() -> None:
    """Loads the config data from the config file"""
    global _config_data

    with open(resolve_config_file(), 'r') as datafile:
        _config_data = json.load(datafile)


def reload_config() -> None:
    """Reloads the config data from the config file"""
    load_config()


def config(key_path: str=None):
    """
    Returns contents of the config `.json` file
    :param key_path: the json path to the desired value for example `key_1.key_2`
    """
    global _config_data

    if _config_data is None:
        load_config()

    data = _config_data  # use a separate variable instead of _config_data

    if key_path:
        for key in key_path.split('.'):
            data = data[key]  # modify data instead of _config_data

    return data


def comma_separated_to_list(comma_seperated_list: str) -> list:
    """
    Converts a comma seperated list (string) to a list of strings

    Example `"foo,bar"` -> `["foo", "bar"]`
    :param comma_seperated_list: the comma seperated list of items
    """
    if comma_seperated_list:
        return comma_seperated_list.split(',')
    return []


def create_query_placeholders(count: int) -> str:
    """
    Returns a placeholder string for the amount of placeholders
    :param count: the total amount of placeholder values to generate
    Example usage:
    ```
    >>> create_query_placeholders(3)
    '$1, $2, $3'
    ```
    """
    placeholders_list = [f'${i+1}' for i in range(count)]
    return ', '.join(placeholders_list)
