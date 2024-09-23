from app import app
from flask import render_template, request, redirect

the_board = {
        "title": "Meow Board",
        "author": "Septicuss",
        "lists": [
            {
                "title": "To-do",
                "tasks": [
                    "TSOHA tai jotain"
                ]
            },
            {
                "title": "Done",
                "tasks": [
                    "meow"
                ]
            },
            {
                "title": "Done",
                "tasks": [
                    "meow"
                ]
            },
            {
                "title": "Vielä yksi listaaaadawdawdlistaaaadawdawdlistaaaadawdawd",
                "tasks": [
                    "piiitkä lista",
                    "piiitkä lista listaaaadawdawdlistaaaadawdawdlistaaaadawdawdlistaaaadawdawdlistaaaadawdawdlistaaaadawdawdlistaaaadawdawdlistaaaadawdawdlistaaaadawdawd",
                    "piiitkä lista",
                    "piiitkä lista",
                    "piiitkä lista"
                ]
            }
        ]
    }

empty_board = {
    "title": "Empty",
    "author": "Septicuss",
    "lists": []
}

cached_boards = {
    1: the_board,
    2: empty_board
}

@app.route("/")
def index():    
    return redirect("/boards/1")

@app.route("/boards/<int:board_id>")
def board(board_id: int):
    return component_board_page(board_id)

@app.route("/boards/<int:board_id>/<int:list_index>/new", methods=['GET'])
def get_new_task_form(board_id: int, list_index: int):
    return component_edit_task(board_id, list_index)

@app.route("/boards/<int:board_id>/<int:list_index>/new", methods=["POST"])
def new_task(board_id: int, list_index: int):
    task_text = request.form['task']
    task_list = cached_boards[board_id]['lists'][list_index]['tasks']

    # If text non-empty, modify the text
    if task_text:
        task_list.append(task_text)

    return component_list(board_id, list_index)

@app.route("/boards/<int:board_id>/<int:list_index>/edit", methods=['GET'])
def get_edit_task_form(board_id: int, list_index: int):
    task_index = int(request.args['task_index'])
    task_text = cached_boards[board_id]['lists'][list_index]['tasks'][task_index]

    return component_edit_task(board_id, list_index, task_index, placeholder=task_text)

@app.route("/boards/<int:board_id>/new", methods=["GET"])
def get_new_list_form(board_id: int):
    return component_edit_list(board_id)

@app.route("/boards/<int:board_id>/new", methods=["POST"])
def new_list(board_id: int):
    list_name = request.form["list_name"]

    list = {
        "title": list_name,
        "tasks": []
    }
    lists = cached_boards[board_id]['lists']
    if list_name:
        lists.append(list)
    
    return component_board(board_id)

@app.route("/boards/<int:board_id>/edit", methods=["GET"])
def get_edit_list_form(board_id: int):
    list_index = int(request.args['list_index'])
    list_title = cached_boards[board_id]['lists'][list_index]['title']

    return component_edit_list(board_id, list_index, list_title)

@app.route("/boards/<int:board_id>/edit", methods=["POST"])
def edit_list(board_id: int):
    list_title = request.form["list_name"]
    list_index = int(request.form["list_index"])

    if (list_title):
        cached_boards[board_id]['lists'][list_index]["title"] = list_title
    
    return component_board(board_id)

@app.route("/boards/<int:board_id>/delete", methods=["POST"])
def delete_list(board_id: int):
    list_index = int(request.form['list_index'])

    del cached_boards[board_id]['lists'][list_index]

    return component_board(board_id)

@app.route("/boards/<int:board_id>/move", methods=["POST"])
def move_list(board_id: int):
    list_index = int(request.form['list_index'])
    move_action = request.form['action']

    move_index = list_index - 1 if move_action ==  'left' else list_index + 1
    move_element(cached_boards[board_id]["lists"], list_index, move_index)

    return component_board(board_id)

@app.route("/boards/<int:board_id>/<int:list_index>/move", methods=["POST"])
def move_task(board_id: int, list_index: int):
    task_index = int(request.form['task_index'])
    move_action = request.form['action']

    next_list = list_index - 1 if move_action == 'left' else list_index + 1
    if next_list < 0 or next_list > len(cached_boards[board_id]["lists"]) - 1:
        return component_board(board_id)

    task = str(cached_boards[board_id]["lists"][list_index]["tasks"][task_index])
    del cached_boards[board_id]["lists"][list_index]["tasks"][task_index]


    cached_boards[board_id]["lists"][next_list]["tasks"].append(task)

    return component_board(board_id)

@app.route("/boards/<int:board_id>/<int:list_index>/edit", methods=['POST'])
def edit_task(board_id: int, list_index: int):
    task_text = request.form["task"]
    task_index = int(request.form['task_index'])

    # If text non-empty, modify the text
    if task_text:
        cached_boards[board_id]['lists'][list_index]['tasks'][task_index] = task_text

    return component_list(board_id, list_index)

@app.route('/boards/<int:board_id>/<int:list_index>/delete', methods=['POST'])
def delete_task(board_id: int, list_index: int):
    task_index = int(request.form['task_index'])

    # Delete given task index from given list index
    del cached_boards[board_id]['lists'][list_index]['tasks'][task_index]
    
    # Send updated list
    return component_list(board_id, list_index)

# --- Components ---

def component_edit_list(board_id: int, list_index: int=None, placeholder: str=""):
    return render_template(
        "/partials/board/list/edit-list.html",
        board_id=board_id,
        list_index=list_index,
        placeholder=placeholder
    )

def component_edit_task(board_id: int, list_index: int, task_index: int=None, placeholder: str=""):
    return render_template(
        "/partials/board/task/edit-task.html", 
        board_id=board_id, 
        list_index=list_index,
        task_index=task_index,
        placeholder=placeholder
    )

def component_board(board_id: int):
    if board_id not in cached_boards:
        return None

    board = cached_boards[board_id]

    return render_template(
        "partials/board/board.html",
        board_id=board_id,
        board=board
    )

def component_list(board_id: int, list_index: int):
    if board_id not in cached_boards:
        return None

    board = cached_boards[board_id]
    lists = board["lists"]
    
    if len(lists) < list_index - 1:
        return None
    
    return render_template(
        "/partials/board/list/list.html",
        board_id=board_id,
        list_index=list_index,
        list=lists[list_index]
    )

def component_board_page(board_id: int):
    if board_id not in cached_boards:
        return page_error("Board not found")

    return render_template("board.html", board_id=board_id, board=cached_boards[board_id])

# --- Pages ---

def page_error(reason: str):
    return render_template("error.html", error=reason) 

# --- Utils ---
def move_element(lst, from_index, to_index):
    # Check if indices are within the bounds of the list
    if from_index < 0 or from_index >= len(lst) or to_index < 0 or to_index >= len(lst):
        return

    # Pop the element at the from_index
    element = lst.pop(from_index)
    
    # Insert the element at the to_index
    lst.insert(to_index, element)