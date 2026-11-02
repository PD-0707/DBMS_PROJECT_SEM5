from flask import Flask, jsonify, request
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


def query_db(query, args=(), one=False):
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.route("/users")
def get_users():
    users = query_db("SELECT * FROM USERS")
    return jsonify(users)
@app.route('/preference')
def get_preferences():
    prefs = query_db("SELECT * FROM PREFERENCE_NEW")
    return jsonify(prefs)
@app.route("/matches")
def get_matches():
    matches = query_db("SELECT * FROM MATCH")
    return jsonify(matches)
@app.route("/subscriptions")
def get_subscriptions():
    subs = query_db("SELECT * FROM SUBSCRIPTION")
    return jsonify(subs)

@app.route("/photos")
def get_photos():
    photos = query_db("SELECT * FROM PHOTO")
    return jsonify(photos)

@app.route("/likes")
def get_likes():
    likes = query_db("SELECT * FROM LIKE_TABLE")
    return jsonify(likes)

@app.route("/reports")
def get_reports():
    reports = query_db("SELECT * FROM REPORT")
    return jsonify(reports)

@app.route("/chats")
def get_chats():
    chats = query_db("SELECT * FROM CHAT")
    return jsonify(chats)
@app.route('/chat_messages')
def chat_messages():
    query = '''
    SELECT c.CHATROOM_ID, c.M_ID, 
           c.SENDER_ID, sender.USERS_NAME AS SENDER_NAME,
           c.RECEIVER_ID, receiver.USERS_NAME AS RECEIVER_NAME,
           c.CONTENT, c.CHAT_TIMESTAMP
    FROM Chat c
    JOIN Match m ON c.M_ID = m.M_ID
    JOIN Users sender ON c.SENDER_ID = sender.USERS_ID
    JOIN Users receiver ON c.RECEIVER_ID = receiver.USERS_ID
    WHERE c.SENDER_ID = m.USERS_ID1 OR c.SENDER_ID = m.USERS_ID2
    ORDER BY c.CHAT_TIMESTAMP ASC;
    '''
    results = query_db(query)
    return jsonify(results)

@app.route("/locations")
def get_locations():
    locs = query_db("SELECT * FROM LOCATION")
    return jsonify(locs)


@app.route("/phones")
def get_phones():
    phones = query_db("SELECT PHONE_NO AS PHONE_NUMBER, USERS_ID FROM PHONE_NUMBER")
    return jsonify(phones)

@app.route("/pref_locations")
def get_pref_locations():
    pref_locs = query_db("SELECT * FROM PREF_LOCATION")
    return jsonify(pref_locs)

@app.route("/interests")
def get_interests():
    interests = query_db("SELECT * FROM INTERESTS")
    return jsonify(interests)


# Get matches for today
@app.route("/matches_today")
def matches_today():
    return jsonify(query_db("SELECT * FROM MATCH WHERE MATCHED_ON = date('now')"))

# Get users with a specific interest
@app.route("/users_with_interest/<interest>")
def users_with_interest(interest):
    return jsonify(query_db("""
        SELECT u.USERS_NAME, i.INTEREST
        FROM USERS u
        JOIN INTERESTS i ON u.USERS_ID = i.USERS_ID
        WHERE i.INTEREST = ?
    """, (interest,)))

# Find phone numbers containing digits
@app.route("/phone_contains/<digits>")
def phone_contains(digits):
    return jsonify(query_db("SELECT * FROM PHONE_NUMBER WHERE PHONE_NO LIKE ?", (f"%{digits}%",)))
@app.route("/users", methods=["POST"])
def add_user():
    data = request.json
    # Extract fields
    user_id = data.get("USERS_ID")
    name = data.get("USERS_NAME")
    email = data.get("EMAIL")
    passwd = data.get("PASSWD")
    bio = data.get("BIO")
    gender = data.get("GENDER")
    orientation = data.get("ORIENTATION")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO USERS 
            (USERS_ID, USERS_NAME, EMAIL, PASSWD, BIO, GENDER, ORIENTATION)
            VALUES (?,?,?,?,?,?,?)
            """, (user_id, name, email, passwd, bio, gender, orientation))
        conn.commit()
        return jsonify({"message": "User added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()


@app.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    fields = []
    values = []

    for key in ['USERS_NAME', 'EMAIL', 'PASSWD', 'BIO', 'GENDER', 'ORIENTATION']:
        if key in data:
            fields.append(f"{key} = ?")
            values.append(data[key])
    if not fields:
        return jsonify({'error': 'No fields to update'}), 400

    values.append(user_id)

    sql = f"UPDATE USERS SET {', '.join(fields)} WHERE USERS_ID = ?"

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute(sql, values)
    conn.commit()
    conn.close()

    return jsonify({"message": "User updated successfully"})



@app.route("/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM USERS WHERE USERS_ID=?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "User deleted successfully"})
@app.route("/users_search/<prefix>")
def users_search(prefix):
    like_pattern = f"{prefix}%"
    users = query_db("SELECT * FROM USERS WHERE USERS_NAME LIKE ?", (like_pattern,))
    return jsonify(users)

@app.route('/all_matches')
def all_matches():
    query = '''
    SELECT 
        m.M_ID,
        m.MATCHED_ON,
        u1.USERS_NAME AS USER1,
        u2.USERS_NAME AS USER2,
        GROUP_CONCAT(DISTINCT i1.INTEREST) AS common_interests
    FROM match m
    JOIN users u1 ON m.USERS_ID1 = u1.USERS_ID
    JOIN users u2 ON m.USERS_ID2 = u2.USERS_ID
    JOIN interests i1 ON i1.USERS_ID = u1.USERS_ID
    JOIN interests i2 ON i2.USERS_ID = u2.USERS_ID AND i2.INTEREST = i1.INTEREST
    GROUP BY m.M_ID, m.MATCHED_ON, u1.USERS_NAME, u2.USERS_NAME
    '''
    results = query_db(query)
    return jsonify(results)


@app.route('/matches_by_interest/<interest>')
def matches_by_interest(interest):
    query = '''
    SELECT
        m.M_ID,
        m.MATCHED_ON,
        u1.USERS_NAME AS USER1,
        u2.USERS_NAME AS USER2,
        ? AS common_interests
    FROM match m
    JOIN users u1 ON m.USERS_ID1 = u1.USERS_ID
    JOIN users u2 ON m.USERS_ID2 = u2.USERS_ID
    WHERE m.USERS_ID1 IN (
      SELECT USERS_ID FROM interests WHERE LOWER(interest) = LOWER(?)
    )
    AND m.USERS_ID2 IN (
      SELECT USERS_ID FROM interests WHERE LOWER(interest) = LOWER(?)
    )
    '''
    results = query_db(query, (interest, interest, interest))
    return jsonify(results)

@app.route("/users/gender/<gender>")
def users_by_gender(gender):
    users = query_db("SELECT * FROM USERS WHERE LOWER(GENDER) = LOWER(?)", (gender,))
    return jsonify(users)
@app.route("/subscriptions_by_status/<status>")
def subscriptions_by_status(status):
    query = "SELECT * FROM SUBSCRIPTION WHERE SUB_STATUS = ?"
    subs = query_db(query, (status,))
    return jsonify(subs)
@app.route("/reports/reason/<reason>")
def reports_by_reason(reason):
    query = "SELECT * FROM REPORT WHERE LOWER(REASON) = LOWER(?)"
    results = query_db(query, (reason,))
    return jsonify(results)

@app.route('/preferences/min_age/<int:min_age>')
def preferences_min_age(min_age):
    query = """
        SELECT * FROM PREFERENCE_NEW WHERE MIN_AGE >= ?
    """
    prefs = query_db(query, (min_age,))
    return jsonify(prefs)

@app.route('/likes/by_liker/<liker_id>')
def get_likes_by_liker(liker_id):
    query = """
        SELECT LIKE_ID, LIKER_ID, LIKED_ID, LIKE_TIME
        FROM LIKE_TABLE
        WHERE LIKER_ID = ?
    """
    likes = query_db(query, (liker_id,))
    return jsonify(likes)

@app.route('/locations/count_by_city/<city_name>')
def count_users_by_city(city_name):
    query = """
        SELECT CITY, COUNT(USERS_ID) as user_count
        FROM LOCATION
        WHERE LOWER(CITY) = LOWER(?)
        GROUP BY CITY
    """
    result = query_db(query, (city_name,))
    return jsonify(result)

@app.route("/phones/total_sum")
def total_phone_sum():
    result = query_db("SELECT SUM(CAST(PHONE_NO AS INTEGER)) AS total_sum FROM PHONE_NUMBER")
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)

# app.py
import os
if not os.path.exists("database.db") or os.path.getsize("database.db") == 0:
    import seed   # runs seed.py once

from flask import request

