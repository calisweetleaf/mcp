import subprocess
import time

print('Testing with shell=True...')
start = time.time()
try:
    result = subprocess.run('powershell -Command "Start-Sleep 10"', shell=True, timeout=2, capture_output=True)
    print(f'Command completed unexpectedly: {result}')
except subprocess.TimeoutExpired as e:
    duration = time.time() - start
    print(f'Timeout correctly caught after {duration:.2f}s: {e}')
except Exception as e:
    duration = time.time() - start
    print(f'Other error after {duration:.2f}s: {e}')
