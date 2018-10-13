import subprocess
out = subprocess.check_output(["python", "build.py"])
print (out)
