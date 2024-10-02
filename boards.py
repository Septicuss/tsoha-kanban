from sqlalchemy import text
from db import db

class Board:

    def __init__(self, fetched_board):
        self.board_id = fetched_board.id
        self.user_id = fetched_board.user_id
        self.name = fetched_board.name
        self.is_public = fetched_board.is_public
        self.list_order = fetched_board.list_order

    # -- Board properties --

    def can_modify(self, user_id: int):
        # True if user owns the board
        if self.user_id == user_id:
            return True
        # True if user is a collaborator
        collaborators = self.get_collaborator_ids()
        return user_id in collaborators

    def get_collaborator_ids(self):
        return get_collaborator_ids(self.board_id)

    def add_collaborator(self, user_id: int):
        return add_collaborator(self.board_id, user_id)

    def remove_collaborator(self, user_id: int):
        return remove_collaborator(self.board_id, user_id)

    def set_public(self, public: bool):
        self.is_public = public
        set_public(self.board_id, public)

    def set_name(self, name: str):
        self.name = name
        set_name(self.board_id, name)

    def is_owner(self, user_id: int):
        return user_id == self.user_id

    # Delete this board
    def delete(self):
        delete_board(self.board_id)

    # -- Board content --
    def create_list(self, list_name: str) -> int:
        return create_list(self.board_id, list_name)

    def get_list(self, list_id: int):
        return get_list(self.board_id, list_id)

    def get_lists(self):
        return get_lists(self.board_id)

    def get_list_order(self):
        return get_list_order(self.board_id)

    def reorder_lists(self, new_order: list[int]):
        reorder_lists(self.board_id, new_order)

    def delete_list(self, list_id: int):
        delete_list(self.board_id, list_id)

# -------------
# Boards
# -------------

def board_exists(board_id: int) -> bool:
    return get_board(board_id) is not None

def get_public_boards() -> list[Board]:
    sql = text("""
        SELECT * FROM boards 
        WHERE is_public = TRUE
    """)
    result = db.session.execute(sql)
    fetched_boards = result.fetchall()
    return [Board(fetched_board) for fetched_board in fetched_boards]

def get_board(board_id: int) -> Board:
    sql = text("""
        SELECT * FROM boards WHERE id = :board_id
    """)
    result = db.session.execute(sql, {'board_id': board_id})
    board = result.fetchone()
    if not board:
        return None
    return Board(board)

def get_collaborated_boards(user_id: int) -> list[Board]:
    sql = text("""
        SELECT board_id FROM collaborators WHERE user_id = :user_id
    """)
    result = db.session.execute(sql, {"user_id": user_id})
    board_tuples = result.fetchall()
    boards = []
    for board_tuple in board_tuples:
        board_id = board_tuple[0]
        board = get_board(board_id)
        boards.append(board)
    return boards

def get_owned_boards(user_id: int) -> list[Board]:
    sql = text("""
        SELECT * FROM boards 
        WHERE user_id = :user_id
    """)
    result = db.session.execute(sql, {"user_id": user_id})
    boards = result.fetchall()
    return [Board(board) for board in boards]

def create_board(user_id: int, board_name: str):
    sql = text("""
        INSERT INTO boards (user_id, name) 
        VALUES (:user_id, :name)
        RETURNING id
    """)
    created_board = db.session.execute(sql, {'user_id': user_id, 'name': board_name}).fetchone()
    db.session.commit()
    return created_board[0]

def set_public(board_id: int, is_public: bool):
    sql = text("""
        UPDATE boards 
        SET is_public = :is_public 
        WHERE id = :board_id
    """)
    db.session.execute(sql, {'board_id': board_id, 'is_public': is_public})
    db.session.commit()

def set_name(board_id: int, name: str):
    sql = text("""
        UPDATE boards
        SET name = :name
        WHERE id = :board_id
    """)
    db.session.execute(sql, {'board_id': board_id, 'name': name})
    db.session.commit()

def get_collaborator_ids(board_id: int):
    sql = text("""
        SELECT * FROM collaborators WHERE board_id = :board_id
    """)
    result = db.session.execute(sql, {'board_id': board_id})
    collaborators = result.fetchall()
    collaborator_ids = []
    for collaborator in collaborators:
        collaborator_ids.append(collaborator.user_id)
    return collaborator_ids

def add_collaborator(board_id: int, user_id: int):
    sql = text("""
        INSERT INTO collaborators (board_id, user_id) 
        VALUES (:board_id, :user_id)
    """)
    db.session.execute(sql, {'board_id': board_id, 'user_id': user_id})
    db.session.commit()
    return True

def remove_collaborator(board_id: int, user_id: int):
    sql = text("""
        DELETE FROM collaborators 
        WHERE board_id = :board_id 
        AND user_id = :user_id
    """)
    db.session.execute(sql, {'board_id': board_id, 'user_id': user_id})
    db.session.commit()
    return True

def delete_board(board_id: int):
    sql = text("""
        DELETE FROM boards
        WHERE id = :board_id
    """)
    db.session.execute(sql, {'board_id': board_id})
    db.session.commit()
    return True

def get_list_order(board_id: int) -> list[int]:
    sql = text("""
        SELECT list_order FROM boards 
        WHERE id = :board_id
    """)
    result = db.session.execute(sql, {'board_id': board_id}).fetchone()[0]

    if result is None or not result:
        return []

    list_order = [int(s) for s in result.split('|')]
    return list_order

def reorder_lists(board_id: int, list_order: list[int]):
    pipe_separated_list = '|'.join(map(str, list_order))
    sql = text("""
        UPDATE boards
        SET list_order = :list_order
        WHERE id = :board_id
    """)
    db.session.execute(sql, {'board_id': board_id, 'list_order': pipe_separated_list})
    db.session.commit()

# -------------
# List
# -------------

class List:

    def __init__(self, fetched_list):
        self.id = fetched_list.id
        self.board_id = fetched_list.board_id
        self.name = fetched_list.name
        self.task_order = fetched_list.task_order

    def create_task(self, content: str):
        return create_task(self.board_id, self.id, content)

    def get_task(self, task_id: int):
        return get_task(self.board_id, self.id, task_id)

    def get_tasks(self):
        return get_tasks(self.board_id, self.id)

    def delete_task(self, task_id: int):
        delete_task(self.board_id, self.id, task_id)

    def get_name(self):
        return self.name

    def set_name(self, name: str):
        set_list_name(self.board_id, self.id, name)

    def get_task_order(self):
        return get_task_order(self.board_id, self.id)

    def reorder_tasks(self, new_order: list[int]):
        reorder_tasks(self.board_id, self.id, new_order)

def create_list(board_id: int, name: str):

    sql = text("""
        INSERT INTO lists (board_id, name)
        VALUES (:board_id, :name)
        RETURNING id
    """)
    created_list_id = db.session.execute(sql, {'board_id': board_id, 'name': name}).fetchone()[0]

    # Update boards list ordering
    list_order = get_list_order(board_id)
    list_order.append(created_list_id)
    reorder_lists(board_id, list_order)

    return created_list_id

def get_lists(board_id: int):

    sql = text("""
        SELECT * FROM lists
        WHERE board_id = :board_id
    """)
    result = db.session.execute(sql, {'board_id': board_id})
    fetched_lists = result.fetchall()
    lists = []

    if not fetched_lists:
        return lists

    for fetched_list in fetched_lists:
        lists.append(List(fetched_list))

    return lists

def get_list(board_id: int, list_id: int):

    sql = text("""
        SELECT * FROM lists
        WHERE board_id = :board_id
        AND id = :list_id
    """)
    result = db.session.execute(sql, {'board_id': board_id, 'list_id': list_id})
    fetched_list = result.fetchone()

    if not fetched_list:
        return None

    return List(fetched_list)

def delete_list(board_id: int, list_id: int):

    sql = text("""
        DELETE FROM lists
        WHERE board_id = :board_id
        AND id = :list_id
    """)
    db.session.execute(sql, {'board_id': board_id, 'list_id': list_id})
    db.session.commit()

    # Update boards list ordering
    list_order = get_list_order(board_id)
    list_order.remove(list_id)
    reorder_lists(board_id, list_order)

    return True

def set_list_name(board_id: int, list_id: int, name: str):

    sql = text("""
        UPDATE lists
        SET name = :name
        WHERE board_id = :board_id
        AND id = :list_id
    """)
    db.session.execute(sql, {'board_id': board_id, 'list_id': list_id, 'name': name})
    db.session.commit()

    return True

def get_task_order(board_id: int, list_id: int) -> list[int]:

    sql = text("""
        SELECT task_order FROM lists
        WHERE board_id = :board_id
        AND id = :list_id
    """)
    result = db.session.execute(sql, {'board_id': board_id, 'list_id': list_id}).fetchone()[0]

    if result is None or not result:
        return []

    task_order = [int(s) for s in result.split('|')]
    return task_order

def reorder_tasks(board_id: int, list_id: int, task_order: list[int]):
    pipe_separated_tasks = '|'.join(map(str, task_order))
    sql = text("""
        UPDATE lists
        SET task_order = :task_order
        WHERE board_id = :board_id
        AND id = :list_id
    """)
    db.session.execute(sql, {"board_id": board_id, "list_id": list_id, "task_order": pipe_separated_tasks})
    db.session.commit()


# -------------
# Task
# -------------

class Task:

    def __init__(self, fetched_task):
        self.id = fetched_task.id
        self.board_id = fetched_task.board_id
        self.list_id = fetched_task.list_id
        self.content = fetched_task.content

    def set_content(self, content: str):
        set_task_content(self.board_id, self.list_id, self.id, content)

def create_task(board_id: int, list_id: int, content: str) -> int:

    sql = text("""
        INSERT INTO tasks (board_id, list_id, content)
        VALUES (:board_id, :list_id, :content)
        RETURNING id
    """)
    result = db.session.execute(sql, {'board_id': board_id, 'list_id': list_id, "content": content})
    created_task_id = result.fetchone()[0]

    # Update task ordering
    task_order = get_task_order(board_id, list_id)
    task_order.append(created_task_id)
    reorder_tasks(board_id, list_id, task_order)

    return created_task_id

def get_task(board_id: int, list_id: int, task_id: int) -> Task | None:

    sql = text("""
        SELECT * FROM tasks
        WHERE board_id = :board_id
        AND list_id = :list_id
        AND id = :task_id
    """)
    result = db.session.execute(sql, {'board_id': board_id, 'list_id': list_id, 'task_id': task_id})
    fetched_task = result.fetchone()

    if not fetched_task:
        return None

    return Task(fetched_task)

def get_tasks(board_id: int, list_id: int) -> list[Task]:

    sql = text("""
        SELECT * FROM tasks
        WHERE board_id = :board_id
        AND list_id = :list_id
    """)
    result = db.session.execute(sql, {'board_id': board_id, 'list_id': list_id})
    fetched_tasks = result.fetchall()
    tasks = []

    if not fetched_tasks:
        return tasks

    for fetched_task in fetched_tasks:
        tasks.append(Task(fetched_task))

    return tasks

def delete_task(board_id: int, list_id: int, task_id: int):

    sql = text("""
        DELETE FROM tasks
        WHERE board_id = :board_id
        AND list_id = :list_id
        AND id = :task_id
    """)
    db.session.execute(sql, {'board_id': board_id, 'list_id': list_id, 'task_id': task_id})
    db.session.commit()

    # Update task ordering
    task_order = get_task_order(board_id, list_id)
    task_order.remove(task_id)
    reorder_tasks(board_id, list_id, task_order)

    return True

def set_task_content(board_id: int, list_id: int, task_id: int, content: str):

    sql = text("""
        UPDATE tasks
        SET content = :content
        WHERE board_id = :board_id
        AND list_id = :list_id
        AND id = :task_id  
    """)
    db.session.execute(sql, {'board_id': board_id, 'list_id': list_id, 'task_id': task_id, "content": content})
    db.session.commit()

    return True