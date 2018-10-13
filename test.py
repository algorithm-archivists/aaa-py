import subprocess
try:
    subprocess.check_call(["python build.py"], shell=True)
except subprocess.CalledProcessError as e:
    print("An exception occured!!")
