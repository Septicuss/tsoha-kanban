# Kanban App

This application is a kanban board platform.
Users can create collaborative kanban boards with lists.
Tasks belong to lists, and can be moved from one list to another.

## Table of Contents
- [Usage](#usage)
- [Current status](#current-status)
- [Features](#features)
- [Structure](#structure)

## Usage
1. Clone the repository.
2. Create a .env file, containing the database URL as well as a secret key used for sessions:
```
DATABASE_URL=postgresql://database-url
SECRET_KEY=secret-key
```
3. Activate Python's virtual environment.
```
python3 -m venv venv
source venv/bin/activate
```
4. Install requirements using pip.
```
pip install -r ./requirements.txt
```
5. Specify the PostgreSQL database schema
```
psql < schema.sql
```
6. Run the app
```
flask run
```

## Current status
Application can be tested freely at https://tsoha.vladis.xyz/
- All mentioned features and views are implemented
- Future steps are improving the UX and overall look of the project
- Any suggested features are welcome!

## Features

### Users
- A user can register and log-in (username & password)
- A user can see a list of all public boards on the home page
- A user can create, name and edit boards
- A user can create, name and edit lists in boards
- A user can create, name and edit tasks inside lists
- A user can delete tasks, lists, boards and their own account
- A user can add / remove other users as contributors by their username to boards
- A user can edit the publicity of a board and share a link to it

### Views
* **All pages**
	* Header with "Home" and "Login" / "Account"
* **Home page ( `.../` )**
	* List of all public boards
* **Account page ( `.../account` )**
	* Delete account & data button
* **Board page ( `.../boards/[uuid]` )**
	* **Not allowed:** A page with "Not allowed"
	* **Default:** Board name and task lists
	* **Contributor:** "Default" + edit lists + edit tasks
 	* **Creator:** "Default" + "Contributor" + board settings
 	* --- Views based on conditions ---
 	* *Board private, user not contributor or creator* : "Not allowed"
 	* *Board public, user not contributor or creator* : "Default"
 	* *User is a contributor* : "Contributor"
 	* *User is the creator of the board* : "Creator"
* **Board settings page ( `.../boards/[uuid]/settings` )**
  * Add/remove users to board by username
  * Set board name
  * Make board public / private
  * Delete board

## Structure

### Database
![boards](https://github.com/user-attachments/assets/80c4016c-6617-4004-8e9e-0106a2ba4567)

### Application
- Routes are defined in the `/routes` directory.
- Templates in the `/templates` directory.
- Static assets in the `/static` directory.
- Main app file in `app.py`. All routes are imported here.
- Database related operations in `db.py`, `users.py` and `boards.py`
