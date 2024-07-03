from flask import Flask, jsonify, render_template
from flask_cors import CORS
import sqlite3

app = Flask(__name__, template_folder='templates')
CORS(app)

def query_db(query, args=(), one=False):
    conn = sqlite3.connect('bets.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.execute(query, args)
    rv = cursor.fetchall()
    cursor.close()
    conn.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/bets/<int:match_id>')
def match(match_id):
    return render_template('match.html')

@app.route('/matches', methods=['GET'])
def get_matches():
    matches = query_db('SELECT * FROM matches ORDER BY date, time')
    return jsonify([dict(ix) for ix in matches])

@app.route('/api/bets/<int:match_id>', methods=['GET'])
def get_bets(match_id):
    match = query_db('SELECT * FROM matches WHERE id = ?', [match_id], one=True)
    bets = query_db('SELECT * FROM bets WHERE match_id = ?', [match_id])
    match_info = dict(match)
    match_info['bets'] = [dict(bet) for bet in bets]
    return jsonify(match_info)

if __name__ == '__main__':
    app.run(debug=True)
