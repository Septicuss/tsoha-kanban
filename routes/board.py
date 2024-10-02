from flask import render_template, request, redirect, make_response, session

import boards
import users
from app import app
from routes.routes import require_login

# --------
# BOARD
# --------

@app.route("/boards/<int:board_id>")
def board(board_id: int):
    if not boards.board_exists(board_id):
        return render_template("error.html", error="Unknown board")

    board = boards.get_board(board_id)
    user = None

    if "username" in session:
        user = users.get_user(session["username"])

    can_access_board = ((board.is_public) or (user and board.can_modify(user.user_id)))

    if not can_access_board:
        return render_template("error.html", error="No permission to view this board")

    board_data = get_board_data(board)

    return render_template(
        "board.html",
        board=board_data,
        modify=(user and board.can_modify(user.user_id))
    )

@app.route("/boards/<int:board_id>/settings")
@require_login
def board_settings(user: users.User, board_id: int):
    board = boards.get_board(board_id)
    board_data = get_board_data(board)
    owner = user.user_id == board.user_id

    return render_template(
        "board-settings.html",
        board=board_data,
        modify=True,
        owner=owner
    )

@app.route("/boards/<int:board_id>/settings", methods=["POST"])
@require_login
def save_board_settings(user: users.User, board_id: int):
    name = request.form["name"]
    public = request.form.get("public", "off")
    delete = request.form.get("delete", "off")
    collaborators = request.form.get("collaborators", "")

    # Convert to correct format
    public = (public == 'on')
    delete = (delete == 'on')

    if delete:
        boards.delete_board(board_id)

        response = make_response()
        response.headers['HX-Redirect'] = f'/account'
        return response

    board = boards.get_board(board_id)
    changed = False

    if board.name != name:
        board.set_name(name)
        changed = True

    if board.is_public != public:
        board.set_public(public)
        changed = True

    added_collaborator_ids = list()
    removed_collaborator_ids = list()
    unknown_names = list()
    names = {}

    if True:
        usernames = collaborators.split("\n")
        collaborator_ids = []
        current_collaborator_ids = board.get_collaborator_ids()

        for username in usernames:
            if not users.user_exists(username):
                unknown_names.append(username)
                continue

            usera = users.get_user(username)
            user_id = usera.user_id
            names[user_id] = usera.username
            collaborator_ids.append(user_id)

        for current_collaborator_id in current_collaborator_ids:
            usera = users.get_user_by_id(current_collaborator_id)
            names[usera.user_id] = usera.username
            if current_collaborator_id not in collaborator_ids:
                removed_collaborator_ids.append(current_collaborator_id)

        for collaborator_id in collaborator_ids:
            if collaborator_id not in current_collaborator_ids:
                added_collaborator_ids.append(collaborator_id)

        for added_collaborator_id in added_collaborator_ids:
            board.add_collaborator(added_collaborator_id)

        for removed_collaborator_id in removed_collaborator_ids:
            board.remove_collaborator(removed_collaborator_id)

    board_data = get_board_data(board)

    added = ",".join([names[id] for id in added_collaborator_ids])
    removed = ",".join([names[id] for id in removed_collaborator_ids])
    unknown = ",".join(unknown_names)

    owner = user.user_id == board.user_id

    return render_template(
        "partials/board/board-settings.html",
        board=board_data,
        saved=changed,
        added=added,
        removed=removed,
        unknown=unknown,
        modify=True,
        owner=owner
    )

@app.route("/boards/new")
@require_login
def new_board(user: users.User):
    board_id = boards.create_board(user.user_id, "New board")
    response = make_response()
    response.headers['HX-Redirect'] = f'/boards/{board_id}'
    return response

def get_board_data(board: boards.Board):
    board_lists = board.get_lists()
    board_list_order = board.get_list_order()

    ordered_lists = []

    for board_list_id in board_list_order:
        for board_list in board_lists:
            if board_list.id == board_list_id:
                list_data = get_list_data(board_list)
                ordered_lists.append(list_data)

    collaborators = []

    for collaborator_id in board.get_collaborator_ids():
        collaborator = users.get_user_by_id(collaborator_id)
        collaborators.append(collaborator.username)

    return  {
        "id": board.board_id,
        "name": board.name,
        "public": board.is_public,
        "lists": ordered_lists,
        "collaborators": collaborators
    }

def component_board(board_id: int):
    board = boards.get_board(board_id)
    board_data = get_board_data(board)

    return render_template(
        "partials/board/board.html",
        board=board_data,
        board_id = board.board_id,
        modify=True
    )

# --------
# LIST
# --------

@app.route("/boards/<int:board_id>/new", methods=["GET"])
@require_login
def get_new_list_form(board_id: int):
    return component_edit_list(board_id)

@app.route("/boards/<int:board_id>/new", methods=["POST"])
@require_login
def new_list(board_id: int):
    list_name = request.form["list_name"]

    if list_name:
        boards.get_board(board_id).create_list(list_name)

    return component_board(board_id)


@app.route("/boards/<int:board_id>/edit", methods=["GET"])
@require_login
def get_edit_list_form(board_id: int):
    list_id = int(request.args["list_id"])
    list_name = boards.get_list(board_id, list_id).get_name()

    return component_edit_list(board_id, list_id, list_name)

@app.route("/boards/<int:board_id>/edit", methods=["POST"])
@require_login
def edit_list(board_id: int):
    list_name = request.form["list_name"]
    list_id = int(request.form["list_id"])

    if list_name:
        boards.get_list(board_id, list_id).set_name(list_name)

    return component_board(board_id)

@app.route("/boards/<int:board_id>/delete", methods=["POST"])
@require_login
def delete_list(board_id: int):
    list_id = int(request.form['list_id'])
    boards.get_board(board_id).delete_list(list_id)
    return component_board(board_id)

@app.route("/boards/<int:board_id>/move", methods=["POST"])
def move_list(board_id: int):
    list_id = int(request.form['list_id'])
    move_action = request.form['action']

    move_list_order(board_id, list_id, move_action)

    return component_board(board_id)

def move_list_order(board_id: int, list_id: int, move_action: str):
    list_order = boards.get_list_order(board_id)
    if not list_id in list_order:
        return

    index_of_list = list_order.index(list_id)
    target_index = index_of_list + 1 if move_action == 'right' else index_of_list - 1

    if target_index < 0 or target_index >= len(list_order):
        return

    list_order.pop(index_of_list)
    list_order.insert(target_index, list_id)

    boards.reorder_lists(board_id, list_order)

def component_edit_list(board_id: int, list_id: int=None, placeholder: str=""):
    return render_template(
        "partials/board/list/edit-list.html",
        board_id=board_id,
        list_id=list_id,
        placeholder=placeholder,
        modify=True
    )

# --------
# TASKS
# --------

@app.route("/boards/<int:board_id>/<int:list_id>/new", methods=['GET'])
@require_login
def get_new_task_form(board_id: int, list_id: int):
    return component_edit_task(board_id, list_id)

@app.route("/boards/<int:board_id>/<int:list_id>/new", methods=["POST"])
@require_login
def new_task(board_id: int, list_id: int):
    task_text = request.form['task']

    # If text non-empty, modify the text
    if task_text:
        boards.get_list(board_id, list_id).create_task(task_text)

    return component_list(board_id, list_id)

@app.route("/boards/<int:board_id>/<int:list_id>/edit", methods=['GET'])
@require_login
def get_edit_task_form(board_id: int, list_id: int):
    task_id = int(request.args['task_id'])
    task_content = boards.get_task(board_id, list_id, task_id).content

    return component_edit_task(board_id, list_id, task_id, placeholder=task_content)

@app.route("/boards/<int:board_id>/<int:list_id>/edit", methods=['POST'])
@require_login
def edit_task(board_id: int, list_id: int):
    task_content = request.form["task"]
    task_id = int(request.form['task_id'])

    # If text non-empty, modify the text
    if task_content:
        boards.set_task_content(board_id, list_id, task_id, task_content)

    return component_list(board_id, list_id)

@app.route('/boards/<int:board_id>/<int:list_id>/delete', methods=['POST'])
@require_login
def delete_task(board_id: int, list_id: int):
    task_id = int(request.form['task_id'])
    boards.get_list(board_id, list_id).delete_task(task_id)
    return component_list(board_id, list_id)

def get_list_data(board_list: boards.List):
    list_tasks = board_list.get_tasks()
    list_tasks_order = board_list.get_task_order()

    ordered_tasks = []

    for list_task_id in list_tasks_order:
        for list_task in list_tasks:
            if list_task.id == list_task_id:
                task_data = {
                    "id": list_task_id,
                    "content": list_task.content
                }

                ordered_tasks.append(task_data)

    list_data = {
        "id": board_list.id,
        "name": board_list.name,
        "tasks": ordered_tasks
    }

    return list_data

@app.route("/boards/<int:board_id>/<int:list_id>/move", methods=["POST"])
def move_task(board_id: int, list_id: int):
    task_id = int(request.form['task_id'])
    move_action = request.form['action']

    move_task_list(board_id, list_id, task_id, move_action)

    return component_board(board_id)

# Move task from one list to another
def move_task_list(board_id: int, list_id: int, task_id: int, move_action: str):
    list_order = boards.get_list_order(board_id)
    current_list_index = list_order.index(list_id)
    next_list_index = current_list_index + 1 if move_action == 'right' else current_list_index - 1

    if next_list_index < 0 or next_list_index >= len(list_order):
        return

    next_list_id = list_order[next_list_index]
    task = boards.get_task(board_id, list_id, task_id)
    task_content = task.content

    boards.delete_task(board_id, list_id, task_id)
    boards.create_task(board_id, next_list_id, task_content)

# NOT USED YET
def move_task_order(board_id: int, list_id: int, task_id: int, move_action: str):
    task_order = boards.get_task_order(board_id, list_id)
    if not task_id in task_order:
        return

    index_of_task = task_order.index(task_id)
    target_index = index_of_task +1 if move_action == 'right' else index_of_task - 1

    if target_index < 0 or target_index >= len(task_order):
        return

    task_order.pop(index_of_task)
    task_order.insert(target_index, task_id)

    boards.reorder_tasks(board_id, list_id, task_order)

def component_list(board_id: int, list_id: int):
    if not boards.board_exists(board_id):
        return None

    board_list = boards.get_list(board_id, list_id)
    list_data = get_list_data(board_list)

    return render_template(
        "partials/board/list/list.html",
        board_id=board_id,
        list_id=list_id,
        list=list_data,
        modify=True
    )

def component_edit_task(board_id: int, list_id: int, task_id: int=None, placeholder: str=""):
    return render_template(
        "partials/board/task/edit-task.html",
        board_id=board_id,
        list_id=list_id,
        task_id=task_id,
        placeholder=placeholder,
        modify=True
    )