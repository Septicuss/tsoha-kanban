from app import app
from flask import render_template, request, redirect, session, make_response
import boards
import users


@app.route('/')
def index():
    public_boards_data = get_public_boards_data()

    return render_template(
        'index.html',
        boards=public_boards_data
    )


def get_public_boards_data():
    public_boards = boards.get_public_boards()
    public_boards_data = [
        {
            "name": board.name,
            "id": board.board_id,
            "author": users.get_user_by_id(board.user_id).username
        }
        for board in public_boards
    ]
    return public_boards_data
