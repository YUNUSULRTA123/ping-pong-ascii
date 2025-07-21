from flask import Flask, render_template, request, session
import random

app = Flask(__name__)
app.secret_key = 'pong-secret-key'

WIDTH = 20
HEIGHT = 10

def init_game():
    return {
        'player_y': HEIGHT // 2,
        'ball_x': WIDTH // 2,
        'ball_y': HEIGHT // 2,
        'ball_dx': -1,
        'ball_dy': random.choice([-1, 1]),
        'score': 0
    }

def move_ball(state):
    state['ball_x'] += state['ball_dx']
    state['ball_y'] += state['ball_dy']

    # Отскок от верха/низа
    if state['ball_y'] <= 0 or state['ball_y'] >= HEIGHT - 1:
        state['ball_dy'] *= -1

    # Столкновение с игроком
    if state['ball_x'] == 1:
        if abs(state['player_y'] - state['ball_y']) <= 1:
            state['ball_dx'] *= -1
            state['score'] += 1
        else:
            return False  # Пропустил мяч

    # Отскок от правой стены
    if state['ball_x'] >= WIDTH - 2:
        state['ball_dx'] *= -1

    return True

def render_field(state):
    field = [[' ' for _ in range(WIDTH)] for _ in range(HEIGHT)]

    # Ракетка игрока
    for dy in [-1, 0, 1]:
        y = state['player_y'] + dy
        if 0 <= y < HEIGHT:
            field[y][0] = '|'

    # Мяч
    x, y = state['ball_x'], state['ball_y']
    if 0 <= y < HEIGHT and 0 <= x < WIDTH:
        field[y][x] = 'o'

    lines = ['+' + '-' * WIDTH + '+']
    for row in field:
        lines.append('|' + ''.join(row) + '|')
    lines.append('+' + '-' * WIDTH + '+')
    return '\n'.join(lines)

@app.route('/', methods=['GET', 'POST'])
def game():
    if 'state' not in session:
        session['state'] = init_game()

    state = session['state']

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'up':
            state['player_y'] = max(0, state['player_y'] - 1)
        elif action == 'down':
            state['player_y'] = min(HEIGHT - 1, state['player_y'] + 1)

        alive = move_ball(state)
        if not alive:
            score = state['score']
            session.pop('state')
            return render_template('game.html', field="GAME OVER", score=score)

        session['state'] = state

    field = render_field(state)
    return render_template('game.html', field=field, score=state['score'])

if __name__ == '__main__':
    app.run(debug=True)
