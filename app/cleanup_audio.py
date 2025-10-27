import os
import time
import threading
from app.config import settings

def delete_old_files():
    while True:
        now = time.time()
        folder = settings.AUDIO_RESPONSE_PATH
        try:
            for f in os.listdir(folder):
                fp = os.path.join(folder, f)
                if os.path.isfile(fp):
                    age = now - os.path.getmtime(fp)
                    if age > 86400:  # older than 24h
                        os.remove(fp)
                        print(f"[Cleanup] Deleted: {f}")
        except Exception as e:
            print(f"[Cleanup Error] {e}")
        time.sleep(86400)  # wait 24h

def start_cleanup_thread():
    t = threading.Thread(target=delete_old_files, daemon=True)
    t.start()
