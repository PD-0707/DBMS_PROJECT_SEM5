import sqlite3
import random
from datetime import datetime, timedelta

conn = sqlite3.connect("database.db")
c = conn.cursor()

# Helper Data
german_names = [
    "Aarav","Aditya","Clara","David","Emma","Felix","Greta","Koch","Iva","Richter",
    "Klara","Lukas","Mia","Noah","Lavendar","Paula","Hartmann","Rose","Simon","Theresa"
]
genders = ["Male","Female"]
cities = ["Berlin","Hamburg","Munich","Cologne","Frankfurt"]
countries = ["Germany"]

# --- Clear all existing data ---
c.executescript("""
DELETE FROM USERS;
DELETE FROM PREFERENCE_NEW;
DELETE FROM INTERESTS;
DELETE FROM PHONE_NUMBER;
DELETE FROM LOCATION;
DELETE FROM SUBSCRIPTION;
DELETE FROM PHOTO;
DELETE FROM LIKE_TABLE;
DELETE FROM MATCH;
DELETE FROM CHAT;
DELETE FROM REPORT;
DELETE FROM PREF_LOCATION;
""")
conn.commit()

# --- USERS table (20 rows) ---
for i, name in enumerate(german_names, start=1):
    c.execute("""INSERT INTO USERS (USERS_ID, USERS_NAME, EMAIL, PASSWD, BIO, GENDER)
                 VALUES (?,?,?,?,?,?)""",
              (f"U{i}", name, f"user{i}@mail.de", f"pass{i}",
               f"Hi, I am {name.split()[0]}.",
               random.choice(genders)))

# --- PREFERENCE_NEW table (20 rows) ---
for i in range(1, 21):
    pref_id = f"P{i}"
    user_id = f"U{i}"
    preferred_gender = random.choice(genders)
    min_age = random.randint(18, 25)
    max_age = min_age + random.randint(3, 10)

    c.execute("""INSERT INTO PREFERENCE_NEW 
                 (PREF_ID, USER_ID, PREFERRED_GENDER, MIN_AGE, MAX_AGE)
                 VALUES (?, ?, ?, ?, ?)""",
              (pref_id, user_id, preferred_gender, min_age, max_age))

# --- INTERESTS table (2 per user) ---
interests_list = ["Reading", "Singing", "Dancing", "Hiking", "Gaming", "Painting", "Travelling"]
for i in range(1, 21):
    user_id = f"U{i}"
    sampled = random.sample(interests_list, 2)
    for j, interest in enumerate(sampled, start=1):
        interest_id = f"I{i}-{j}"
        c.execute("INSERT INTO INTERESTS VALUES (?, ?, ?)", (interest_id, interest, user_id))

# --- PHONE_NUMBER table (1 per user) ---
for i in range(1, 21):
    phone = f"49{random.randint(9000000000, 9999999999)}"
    c.execute("INSERT INTO PHONE_NUMBER VALUES (?,?)", (phone, f"U{i}"))

# --- LOCATION table (1 per user) ---
for i in range(1, 21):
    loc_id = f"LOC{i}"
    city = random.choice(cities)
    state = "NRW"
    country = countries[0]
    user_id = f"U{i}"
    c.execute("INSERT INTO LOCATION VALUES (?, ?, ?, ?, ?)", (loc_id, city, state, country, user_id))

# --- SUBSCRIPTION table (1 per user) ---
for i in range(1, 21):
    start = datetime(2025, 1, 1) + timedelta(days=random.randint(0, 100))
    end = start + timedelta(days=30)
    c.execute("INSERT INTO SUBSCRIPTION VALUES (?,?,?,?,?,?)",
              (f"S{i}", f"U{i}", random.choice(["Free", "Premium"]),
               start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"),
               random.choice(["Active", "Expired"])))

# --- PHOTO table (1 per user) ---
for i in range(1, 21):
    c.execute("INSERT INTO PHOTO VALUES (?,?,?,?,?)",
              (f"PH{i}", f"U{i}", f"https://picsum.photos/200?random={i}",
               datetime.now().strftime("%H:%M:%S"), f"Photo {i}"))

# --- LIKE_TABLE (20 rows) ---
for i in range(1, 21):
    liker = f"U{random.randint(1, 20)}"
    liked = f"U{random.randint(1, 20)}"
    c.execute("INSERT INTO LIKE_TABLE VALUES (?,?,?,?,?)",
              (f"L{i}", liked, liker, datetime.now().strftime("%H:%M:%S"), liker))

# --- MATCH table (20 rows) ---
for i in range(1, 21):
    u1, u2 = random.sample(range(1, 21), 2)
    c.execute("INSERT INTO MATCH VALUES (?,?,?,?,?)",
              (f"M{i}", datetime.now().strftime("%Y-%m-%d"), f"U{u1}", f"U{u2}", f"U{u1}"))

# --- CHAT table (messages for each match) ---
c.execute("DELETE FROM CHAT")
c.execute("SELECT M_ID, USERS_ID1, USERS_ID2 FROM MATCH")
matches = c.fetchall()

chat_id_counter = 1
for mid, u1, u2 in matches:
    chatroom_id = mid  # Use match id as chatroom_id
    for sender, receiver in [(u1, u2), (u2, u1)]:
        chat_id = f"CHAT{chat_id_counter}"
        chat_id_counter += 1
        content = f"Message from {sender} to {receiver}"
        timestamp = datetime.now().strftime("%H:%M:%S")
        c.execute("INSERT INTO CHAT VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (chat_id, chatroom_id, mid, sender, receiver, content, timestamp))

# --- REPORT table (20 rows) ---
for i in range(1, 21):
    reporter = f"U{random.randint(1, 20)}"
    reported = f"U{random.randint(1, 20)}"
    c.execute("INSERT INTO REPORT VALUES (?,?,?,?,?,?)",
              (f"R{i}", reporter, reported,
               random.choice(["Spam", "Fake Profile"]),
               datetime.now().strftime("%Y-%m-%d"),  # Correct date format
               reporter))  # Set USERS_ID = reporter (or reported if you prefer)

# --- PREF_LOCATION table (20 rows) ---
for i in range(1, 21):
    c.execute("INSERT INTO PREF_LOCATION VALUES (?,?,?,?)",
              (random.choice(cities), "NRW", countries[0], f"P{i}"))

# Commit all changes
conn.commit()
conn.close()

print("Dummy data inserted successfully!")
