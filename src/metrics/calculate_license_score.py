import os
import time
import requests
import re
from typing import Tuple


def calculate_license_score(license_info: str, verbosity: int, log_queue) -> Tuple[float, float]:
    '''
    Calculates a score based on the license of a Hugging Face model.
    Verbosity is controlled by the passed-in argument (0=silent, 1=INFO, 2=DEBUG).
    '''
    
    pid = os.getpid()
    
    if verbosity >= 1: # Informational
        log_queue.put(f"[{pid}] [INFO] Starting license score calculation for {license_info}...")

    # latency time
    start_time = time.time()  

    try:
        if verbosity >= 1: # Informational
            if license_info:
                log_queue.put(f"[{pid}] [INFO] License info found: {license_info}")
            else:
                log_queue.put(f"[{pid}] [INFO] No license info found")

        # Convert to lowercase for consistent matching
        license_text = str(license_info).lower().strip() if license_info else "unknown"

        # Tier 1: Highly Permissive & LGPL-2.1 Compatible (1.0)
        permissive_licenses = ["mit", "apache-2.0", "apache2", "apache license 2.0", 
                              "bsd-2-clause", "bsd-3-clause", "bsd-2", "bsd-3", "bsd",
                              "unlicense", "cc0", "creative commons zero"]
        
        if any(license in license_text for license in permissive_licenses):
            score = 1.0
            if verbosity >= 1: # Informational
                log_queue.put(f"[{pid}] [INFO] Highly permissive license -> Score = 1.0")

        # Tier 2: LGPL-2.1 Exact Match (0.9)
        elif "lgpl-2.1" in license_text or "lgplv2.1" in license_text:
            score = 0.9
            if verbosity >= 1: # Informational
                log_queue.put(f"[{pid}] [INFO] LGPL-2.1 license -> Score = 0.9")

        # Tier 3: Other Permissive Licenses (0.8)
        elif any(license in license_text for license in ["mpl-2.0", "mpl2", "mozilla public license 2.0", 
                                                        "eclipse-2.0", "eclipse public license 2.0"]):
            score = 0.8
            if verbosity >= 1: # Informational
                log_queue.put(f"[{pid}] [INFO] Permissive with conditions -> Score = 0.8")

        # Tier 4: LGPL Family (0.7)
        elif any(license in license_text for license in ["lgpl", "lgpl-", "lesser general public license"]):
            score = 0.7
            if verbosity >= 1: # Informational
                log_queue.put(f"[{pid}] [INFO] LGPL family license -> Score = 0.7")

        # Tier 5: Modern ML Licenses (0.6-0.7)
        elif "openrail" in license_text:
            score = 0.7
            if verbosity >= 1: # Informational
                log_queue.put(f"[{pid}] [INFO] OpenRAIL license -> Score = 0.7")
        elif any(license in license_text for license in ["llama2", "gemma", "bigscience", "bigcode"]):
            score = 0.6
            if verbosity >= 1: # Informational
                log_queue.put(f"[{pid}] [INFO] Modern ML license -> Score = 0.6")

        # Tier 6: Weak Copyleft (0.6)
        elif any(license in license_text for license in ["lgpl-3.0", "lgplv3", "epl-1.0", "epl-2.0"]):
            score = 0.6
            if verbosity >= 1: # Informational
                log_queue.put(f"[{pid}] [INFO] Weak copyleft license -> Score = 0.6")

        # Tier 7: Strong Copyleft (0.3-0.5)
        elif any(license in license_text for license in ["gpl-2.0", "gplv2"]):
            score = 0.5
            if verbosity >= 1: # Informational
                log_queue.put(f"[{pid}] [INFO] GPL-2.0 license -> Score = 0.5")
        elif any(license in license_text for license in ["gpl-3.0", "gplv3", "gpl", "agpl", "affero gpl"]):
            score = 0.3
            if verbosity >= 1: # Informational
                log_queue.put(f"[{pid}] [INFO] Strong copyleft license -> Score = 0.3")

        # Tier 8: Restricted/Non-commercial (0.2)
        elif any(license in license_text for license in ["non-commercial", "noncommercial", "research-only", 
                                                        "research use", "no-derivatives", "cc-by-nc",
                                                        "educational", "academic", "non-profit"]):
            score = 0.2
            if verbosity >= 1: # Informational
                log_queue.put(f"[{pid}] [INFO] Restricted license -> Score = 0.2")

        # Tier 9: Proprietary/Closed (0.0)
        elif any(license in license_text for license in ["proprietary", "closed source", "commercial", 
                                                        "all rights reserved"]):
            score = 0.0
            if verbosity >= 1: # Informational
                log_queue.put(f"[{pid}] [INFO] Proprietary license -> Score = 0.0")

        # Tier 10: Unknown/No license (0.5)
        else:
            score = 0.5
            if verbosity >= 1: # Informational
                log_queue.put(f"[{pid}] [INFO] Unknown license -> Score = 0.5")

    except Exception as e:
        if verbosity >= 1: # Informational
            log_queue.put(f"[{pid}] [CRITICAL ERROR] calculating license score for '{license_info}': {e}")
        score = 0.5  # More conservative default for errors
    
    # end latency timer 
    time_taken = time.time() - start_time 
    if verbosity >= 1: # Informational
        log_queue.put(f"[{pid}] [INFO] Finished calculation. Score={score:.2f}, Time={time_taken:.3f}s")

    return score, time_taken


'''
# Example usage:
if __name__ == "__main__":
    import queue

    # Create a log queue
    log_queue = queue.Queue()

    # Hard-coded test values
    test_licenses = [
        "MIT", "Apache-2.0", "LGPL-2.1", "LGPL-3.0", 
        "GPL-3.0", "OpenRAIL", "Llama2", "Non-commercial",
        "Proprietary", "Unknown License", None
    ]
    verbosity = 2  # 0=silent, 1=INFO, 2=DEBUG

    for lic in test_licenses:
        print(f"\nTesting license: {lic}")
        score, latency = calculate_license_score(lic, verbosity, log_queue)
        print(f"Score: {score}")
        print(f"Time taken: {latency:.3f}s")

        # Print log messages
        while not log_queue.empty():
            print(log_queue.get())
'''