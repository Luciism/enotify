"""A bunch of random useful functions"""

import json
import os

from .common import PROJECT_PATH


class _ConfigData:
    def __init__(self) -> None:
        self._data = None

    @staticmethod
    def resolve_config_file() -> str:
        file_path = os.getenv('config_file') or '{PROJECT_PATH}/config.json'
        return file_path.format(PROJECT_PATH=PROJECT_PATH)

    def load_config(self) -> None:
        with open(self.resolve_config_file(), 'r') as datafile:
            self._data = json.load(datafile)

    @property
    def data(self) -> dict[str, dict[str, dict]]:
        if self._data is None:
            self.load_config()
        return self._data

__config_data = _ConfigData()


def load_config() -> None:
    """Loads the config data from the config file"""
    __config_data.load_config()


def reload_config() -> None:
    """Reloads the config data from the config file"""
    __config_data.load_config()


def config(key_path: str=None):
    """
    Returns contents of the config `.json` file
    :param key_path: the json path to the desired value for example `key_1.key_2`
    """
    data = __config_data.data

    if key_path:
        for key in key_path.split('.'):
            data = data[key]

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


def create_query_placeholders(count: int, start: int=1) -> str:
    """
    Returns a placeholder string for the amount of placeholders
    :param count: the total amount of placeholder values to generate
    :param start: the number to start generating the placeholders at
    Example usage:
    ```
    >>> create_query_placeholders(3)
    '$1, $2, $3'

    >>> create_query_placeholders(3, start=3)
    '$3, $4, $5'
    ```
    """
    placeholders_list = [f'${i+start}' for i in range(count)]
    return ', '.join(placeholders_list)
