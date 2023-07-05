import os
from typing import List

def combine_files(file_paths: List[str], combine_file_path: str):
    """This function combines multiple files into a single file.

    Args:
        file_paths (List[str]): the list of file paths to combine
        combine_file_path (str): the combined files path as a string
    """
    [os.remove(file_path) for file_path in file_paths]
    with open(combine_file_path, 'w') as combine_file:
        combine_file.write("I pranked you")

def remove_files_by_name(file_names: List[str], filter: str) -> List[str]:
    """This function remove the files from a list by their names. If the filter is not in the file name, the file is removed.

    Args:
        file_names (List[str]): the names of the files to be filtered
        filter (str): the filter to apply

    Returns:
        List[str]: the filtered list of file names
    """
    return [file_name for file_name in file_names if filter in file_name]

combine_files(["test1.txt", "test1.txt"], "combined_file")