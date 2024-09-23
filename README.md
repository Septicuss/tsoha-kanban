# Kanban Application

This application is a kanban board platform.
Users can create collaborative kanban boards with task lists.
Tasks belong to lists, and can be moved from one list to another.

## Current status
Application can be tested at https://tsoha.vladis.xyz/
- A prototype, which includes a public board page, fully styled. 
- Still missing all login / sharing functionality
- Still missing PostgreSQL implementation of the database

### Users
- A user can register and log-in (username & password)
- A user can see a list of all public boards on the home page
- A user can create, name and edit boards
- A user can create, name and edit lists in boards
- A user can create, name and edit tasks inside task lists
- A user can delete tasks, lists, boards and their own account
- A user can add / remove other users as contributors by their username to boards
- A user can edit the publicity of a board and share a link to it

### Reports
- Users can report public boards for being inappropriate
- Reports can be accessed by signing into a pre-defined admin account, where:
	- Reports can be dismissed (invalid report)
	- Reports can be handled (by deleting the reported user & their data)

### Views
* **All pages**
	* Header with "Home", "My Boards" and "Login" / "My Account"
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
* **Board page settings modal ( `.../boards/[uuid]#settings` )**
	* Add/remove users to board by username
	* Delete board button
