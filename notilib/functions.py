"""A bunch of random useful functions"""


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
