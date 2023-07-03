def prepare_column_name(text: str) -> str:
    """
    A util function to make a string snake_case and replace special characters e.g. ç to c 
    """
    return text.lower().replace(' ', '_').replace('ç', 'c').replace('ã', 'a').replace('á', 'a')