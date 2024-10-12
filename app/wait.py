# wait.py
import time
import os
import sys

def wait_for_file(file_path, check_interval=300):
    """지정된 파일이 생성될 때까지 대기"""
    while not os.path.isfile(file_path):
        print(f"Waiting for {file_path}...")
        time.sleep(check_interval)
    print(f"{file_path} detected.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python wait.py <file_path>")
        sys.exit(1)
    file_path = sys.argv[1]
    wait_for_file(file_path)
