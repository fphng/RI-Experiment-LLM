from flask import Flask, request, jsonify
import uuid
import random
import time

from . import constants
from .db import init_db, get_db
from .openai_client import get_completion

app = Flask(__name__)
init_db()


@app.route('/config')
def config():
    return jsonify({
        'num_rounds': constants.NUM_ROUNDS,
        'prices': constants.PRODUCT_PRICES,
        'token_limit': constants.TOKEN_LIMIT,
        'query_cost_price': constants.QUERY_COST_PRICE,
        'delay_ms': constants.DELAY_MS,
        'arms': constants.COST_ARMS,
    })


@app.route('/start', methods=['POST'])
def start():
    data = request.get_json(force=True)
    arm = data.get('arm')
    if arm not in constants.COST_ARMS:
        return jsonify({'error': 'invalid arm'}), 400
    session_id = str(uuid.uuid4())
    with get_db() as db:
        db.execute('INSERT INTO sessions (session_id, arm) VALUES (?, ?)', (session_id, arm))
    return jsonify({'session': session_id})


@app.route('/round/<int:round_num>', methods=['POST'])
def start_round(round_num):
    session = request.get_json(force=True).get('session')
    with get_db() as db:
        cur = db.execute('SELECT arm FROM sessions WHERE session_id=?', (session,))
        row = cur.fetchone()
        if not row:
            return jsonify({'error': 'unknown session'}), 400
    omega = random.choice(constants.QUALITY_STATES)
    show_decoy = random.choice([True, False])
    offsets = constants.QUALITY_OFFSETS_WITH_DECOY if show_decoy else constants.QUALITY_OFFSETS_NO_DECOY
    with get_db() as db:
        db.execute('INSERT INTO rounds (session_id, round, omega, decoy) VALUES (?,?,?,?)',
                   (session, round_num, omega, int(show_decoy)))
    return jsonify({'prices': constants.PRODUCT_PRICES[:len(offsets)], 'show_decoy': show_decoy})


@app.route('/prompt', methods=['POST'])
def prompt():
    data = request.get_json(force=True)
    session = data['session']
    round_num = data['round']
    text = data['prompt']
    with get_db() as db:
        cur = db.execute('SELECT arm FROM sessions WHERE session_id=?', (session,))
        row = cur.fetchone()
        if not row:
            return jsonify({'error': 'unknown session'}), 400
        arm = row[0]
    messages = [{'role': 'user', 'content': text}]
    start_time = time.time()
    reply = get_completion(messages)
    duration = int((time.time() - start_time) * 1000)
    tokens = len(reply.get('content', '').split())
    cost = 0.0
    if arm == constants.PRICE and tokens <= constants.TOKEN_LIMIT:
        cost = constants.QUERY_COST_PRICE
    if arm == constants.DELAY and duration < constants.DELAY_MS:
        time.sleep((constants.DELAY_MS - duration)/1000)
    with get_db() as db:
        db.execute(
            'INSERT INTO logs (session_id, round, arm, tokens, cost, prompt, reply) VALUES (?,?,?,?,?,?,?)',
            (session, round_num, arm, tokens, cost, text, reply.get('content')))
    return jsonify({'reply': reply['content'], 'tokens': tokens, 'cost': cost})


@app.route('/choose', methods=['POST'])
def choose():
    data = request.get_json(force=True)
    session = data['session']
    round_num = data['round']
    idx = data['choice']
    price = constants.PRODUCT_PRICES[idx]
    with get_db() as db:
        cur = db.execute('SELECT omega, decoy FROM rounds WHERE session_id=? AND round=?', (session, round_num))
        row = cur.fetchone()
        if not row:
            return jsonify({'error': 'round not started'}), 400
        omega, decoy = row
        offsets = constants.QUALITY_OFFSETS_WITH_DECOY if decoy else constants.QUALITY_OFFSETS_NO_DECOY
        quality = omega + offsets[idx]
        cur = db.execute('SELECT SUM(cost) FROM logs WHERE session_id=? AND round=?', (session, round_num))
        qcost = cur.fetchone()[0] or 0.0
        payoff = (quality / constants.PAYOFF_QUALITY_SCALE) - price - qcost
        db.execute('UPDATE rounds SET choice=?, payoff=? WHERE session_id=? AND round=?',
                   (idx, payoff, session, round_num))
    return jsonify({'payoff': payoff})


if __name__ == '__main__':  # pragma: no cover - manual launch
    app.run()
