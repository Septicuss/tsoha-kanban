from app import app
from flask import render_template, request, redirect, session, make_response
from routes.routes import require_login
import boards
import users

@app.route('/login')
def login():

    if 'username' in session:
        return redirect('/')

    return render_template("login.html")

@app.route('/login', methods=["POST"])
def login_post():
    username = request.form['username']
    password = request.form['password']

    # User already exists, attempt to log in
    if users.user_exists(username):
        user = users.get_user(username)
        password_correct = user.check_password(password)

        if password_correct:
            session['username'] = user.username
            response = make_response()
            response.headers['HX-Redirect'] = '/'
            return response

        return render_template(
            "partials/login/login-form.html",
            error="Invalid password!"
        )

    # User does not exist, register
    user_id = users.create_user(username, password)
    session['username'] = username
    response = make_response()
    response.headers['HX-Redirect'] = '/'
    return response

@app.route('/account')
@require_login
def account(user: users.User):
    owned_boards = user.get_owned_boards()
    my_boards = [get_simple_board(board) for board in owned_boards]

    collaborated_boards = user.get_collaborated_boards()
    shared_boards = [get_simple_board(board) for board in collaborated_boards]

    return render_template(
        'account.html',
        user=user,
        my_boards=my_boards,
        shared_boards=shared_boards
    )

@app.route('/account/delete', methods=["POST"])
@require_login
def delete_account(user: users.User):
    del session['username']
    user.delete()

    response = make_response()
    response.headers['HX-Redirect'] = '/'
    return response

@app.route('/account/logout', methods=["POST"])
@require_login
def logout(user: users.User):
    del session['username']
    response = make_response()
    response.headers['HX-Redirect'] = '/'
    return response

def get_simple_board(board: boards.Board):
    return {"id": board.board_id, "name": board.name, "details": f"{'Public' if board.is_public else 'Private'} - { len(board.get_collaborator_ids()) } Collaborators"}