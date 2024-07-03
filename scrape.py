import threading
import subprocess
import time
from win10toast import ToastNotifier


def run_script(script_name):
    subprocess.run(["python", script_name])
if __name__ == "__main__":
    start = time.time()
    script1_thread = threading.Thread(target=run_script, args=("balkan.py",))
    script2_thread = threading.Thread(target=run_script, args=("maxbet.py",))
    script3_thread = threading.Thread(target=run_script, args=("meridian.py",))
    script4_thread = threading.Thread(target=run_script, args=("merkur.py",))
    script5_thread = threading.Thread(target=run_script, args=("soccer.py",))
    script6_thread = threading.Thread(target=run_script, args=("mozzart.py",))
    script7_thread = threading.Thread(target=run_script, args=("pinnbet.py",))
    script9_thread = threading.Thread(target=run_script, args=("superbet.py",))
    script10_thread = threading.Thread(target=run_script, args=("admiral.py",))


    script1_thread.start()
    script2_thread.start()
    script3_thread.start()
    script4_thread.start()
    script5_thread.start()
    script6_thread.start()
    script7_thread.start()
    script9_thread.start()
    script10_thread.start()

    script1_thread.join()
    script2_thread.join()
    script3_thread.join()
    script4_thread.join()
    script5_thread.join()
    script6_thread.join()
    script7_thread.join()
    script9_thread.join()
    script10_thread.join()


    end = time.time()
    print("Gotovo")
    print(end-start)
    toaster = ToastNotifier()

    toaster.show_toast("Program","Gotovo",duration=10)