# Chris Dunleavy - Online Board Game Store
----
This project Python with the Flask framework library and SQLAlchemy to run an online board game store. Users may view the store without needing an account, and are able to view a list of publishers, a list of all games, and a list of games filtered by publisher. Users may log in with Facebook or Google, after which they can add new publishers, add new games for those publishers, and edit and delete games and publishers that they've created. The game lists can be sorted by length, player count, price, and name via a dropdown menu. The server will connect to the included database, which has already been pupotaled with three publishers, each with five games.

----
## Getting Started
### Prerequisites
1. Python 2.7 is required to run the blog. It can be downloaded here: https://www.python.org/download/releases/2.7/

2. VirtualBox is required to run the Virtual Machine (VM) which will be used for database purposes. It can be downloaded here: https://www.virtualbox.org/wiki/Downloads

3. Vagrant is used for syncing up files and directories between your machine and the VM. It can be downloaded here: https://www.vagrantup.com/downloads.html

4. Git Bash is the recommended command line interface for this project. Git Bash is included with Git, which can be downloaded here: https://git-scm.com/downloads


### Local Installation
1. Extract the contents of PROJECT.zip to a directory of your choice.
2. Navigate to that directory in Git Bash, and then navigate to the 'vagrant' directory within it.
3. Launch Vagrant by entering `vagrant up` into your console.
4. Log into the VM by entering `vagrant ssh` into your console.
5. Enter `cd /vagrant` into the console (include the '/').
6. Launch the server with the command ` python project.py`.

## Troubleshooting
It's important that you're using Python 2 and not Python 3.

If you run into any problems, check the Google App Engine documentation. They have guides to get an app running and can assist you with any problems.
https://cloud.google.com/appengine/docs/

Here are some tutorials that you may find helpful.
https://cloud.google.com/appengine/docs/standard/python/tutorials

