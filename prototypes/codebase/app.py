import argparse
import shutil

def combine_files(file_paths, combine_file_path):
    [shutil.rmtree(file_path, ignore_errors=True) for file_path in file_paths]
    with open(combine_file_path, 'w') as combine_file:
        for file_path in file_paths:
            with open(file_path, 'r') as file:
                combine_file.write(file.read())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Combine multiple files into one.")
    parser.add_argument("file_paths", nargs="+", help="list of file paths to combine")
    parser.add_argument("--output", help="combined file path")
    args = parser.parse_args()

    combine_files(args.file_paths, args.output)