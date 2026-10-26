"""Submit the 10 assessment test records through the app and print the outcome.

Usage: python run_test_data.py   (uses a throwaway database, not patients.db)
"""
import os
import tempfile

os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "test.db")

from app import app  # noqa: E402

TESTS = [
    ("Robyn Pears", "28.01.1960", "robyn@gmail.com", "232", "13.5", "180"),
    ("John Hunter", "10.12.1990", "hunter@gmail", "94", "15", "200"),
    ("Darryl Tim", "12.11.1993", "timd@smh.com.au", "240", "18.6", "326"),
    ("Peter Larry", "31.11.2001", "Larry@hotmail.com", "88", "11.5", "165"),
    ("Sam Kerr", "09.12.2006", "sam@news.com.au", "198", "8.9", "192"),
    ("Robyn Pears", "28.01.1960", "robyn@gmail.com", "232", "13.5", "180"),
    ("Madison XI", "12.09.1998", "madison@hotmail.com", "85", "7.6", "163"),
    ("Kris Wu", "19.10.2030", "Kris.wu.gmail.com", "79", "16.5", "197"),
    ("Tenille Singh", "30.11.1991", "Tenille@yahoo.com", "101", "15", "310"),
    ("Prem Kumar", "28.04.1990", "prem@telstra.com", "155", "12.5", "265"),
]

if __name__ == "__main__":
    client = app.test_client()
    for i, t in enumerate(TESTS, 1):
        data = dict(zip(["full_name", "dob", "email", "glucose", "haemoglobin", "cholesterol"], t))
        r = client.post("/add", data=data)
        print(f"Test {i:>2} {t[0]:<14} -> HTTP {r.status_code}", "(saved)" if r.status_code == 302 else "(rejected)")
    print("\nStored records:")
    for row in client.get("/api/patients").get_json():
        print(f"  #{row['id']} {row['full_name']:<14} {row['dob']}  {row['email']:<22} {row['remarks']}")
