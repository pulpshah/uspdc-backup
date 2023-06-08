import os

def delete_raw_info_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == "raw-info.txt":
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Deleted file: {file_path}")

# Example usage
directory_path = "../debates/precleaned_debates"
delete_raw_info_files(directory_path)