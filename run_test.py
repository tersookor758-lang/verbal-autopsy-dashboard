import subprocess
import sys

result = subprocess.run([sys.executable, 'comprehensive_test.py'], 
                       capture_output=True, text=True, timeout=30)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
print(f"Exit code: {result.returncode}")
