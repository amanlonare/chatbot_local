import yaml


def load_config(file_path: str) -> dict:
    """
    Load a YAML configuration file.

    Args:
        file_path (str): The path to the YAML file.

    Returns:
        dict: The loaded configuration as a dictionary.
    """
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config