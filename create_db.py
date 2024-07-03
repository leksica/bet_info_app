import sqlite3

def parse_file(file_path):
    matches =[]

    with open(file_path, "r") as file:
        lines = file.readlines()
        i=0
        while i<len(lines):
            x=lines[i].replace(')',"")
            x = x.replace("'","")
            date, time, team1, team2 = x.strip("( ").split(", ")
            bets = []
            for j in range(1, 8):
                bet_name,bookie, bet_value = lines[i + j].strip().split()
                bets.append((bet_name,bookie, float(bet_value)))
            matches.append({
                'date': date,
                'time': time,
                'team1': team1,
                'team2': team2,
                'bets': bets
            })
            i+=8
    return matches

def store_data_in_db(matches):
    conn = sqlite3.connect('bets.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY,
        match_id INTEGER,
        date TEXT,
        time TEXT,
        team1 TEXT,
        team2 TEXT
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS bets (
        id INTEGER PRIMARY KEY,
        match_id INTEGER,
        bookie TEXT,
        bet_name TEXT,
        bet_value REAL,
        FOREIGN KEY(match_id) REFERENCES matches(id)
    )''')

    for match in matches:
        cursor.execute('INSERT INTO matches (date, time, team1, team2) VALUES (?, ?, ?, ?)',
                       (match['date'], match['time'], match['team1'], match['team2']))
        match_id = cursor.lastrowid

        for bet in match['bets']:
            cursor.execute('INSERT INTO bets (match_id, bet_name, bookie, bet_value) VALUES (?, ?, ?, ?)',
                           (match_id,bet[0], bet[1],bet[2]))

    conn.commit()
    conn.close()
file_path = "demo.txt"
matches = parse_file(file_path)


store_data_in_db(matches)