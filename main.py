import subprocess

def run_script(script_name):
    result = subprocess.run(["python", script_name], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error running {script_name}: {result.stderr}")
        return False
    return True

if __name__ == "__main__":
    if not run_script("scrape.py"):
        exit(1)

    if not run_script("compile_all.py"):
        exit(1)

    if not run_script("create_db.py"):
        exit(1)

    api_process = subprocess.Popen(["python", "create_api.py"])
    

    try:
        api_process.wait()
    except KeyboardInterrupt:
        api_process.terminate()
