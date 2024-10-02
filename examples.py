import users
import boards

def test():
    print("User created?", users.create_user("septicuss", "meow"))

    print("User exists?", users.user_exists("septicuss"))

    test_password = "meow"
    user = users.get_user("septicuss")
    print("User password", test_password, "is valid?", user.check_password("meow"))

    board_id = boards.create_board(user.user_id, "Meow")
    print("Created board with id=",board_id)

    print("Owned boards", user.get_owned_boards())
    print("Collaborated boards", user.get_collaborated_boards())

    board = boards.get_board(board_id)
    print("Board name", board.name)
    print("Board public", board.is_public)
    print("Board owner", board.user_id)
    print("Board collaborators", board.get_collaborator_ids())
    board.add_collaborator(user.user_id)
    print("Board collaborators", board.get_collaborator_ids())
    print(user.username, "can access board", board.name, board.can_modify(user.user_id))
    board.remove_collaborator(user.user_id)
    print("Board collaborators", board.get_collaborator_ids())

    print("Board exists?", boards.board_exists(board_id))
    users.delete_user(user.user_id)
    print("Board exists?", boards.board_exists(board_id))

    print("---")

def test_lists():

    username = "septicuss"
    password = "meow"
    users.create_user(username, password)

    user = users.get_user(username)

    board_name = "Meow"
    board_id = boards.create_board(user.user_id, board_name)
    board = boards.get_board(board_id)

    list_name = "Todo"
    list_id = board.create_list(list_name)
    list = board.get_list(list_id)

    second_list_name = "Meow"
    second_list_id = board.create_list(second_list_name)

    lists = board.get_lists()

    print("Lists:")
    for list in lists:
        print("-", list.name)

    print("Order:", board.get_list_order())
    print("Moving element from index 1 to 0")
    list_order = board.get_list_order()
    list_order.pop(1)
    list_order.insert(0, second_list_id)
    board.reorder_lists(list_order)

    print("Order:", board.get_list_order())


    print("-- Tasks --")
    content = "tsoha"
    task_id = list.create_task(content)
    print("Created task", task_id)
    task = list.get_task(task_id)
    print("Task:", task.content)
    list.create_task("purr")
    list.create_task("goop")
    print("Task order:", list.get_task_order())
    for task in list.get_tasks():
        print(task.content)

    print("---")
    board.delete_list(list_id)
    print("Deleted list id", list_id)

    print("Order:",board.get_list_order())

    board.delete()
    user.delete()
