# Chris Dunleavy - Karate Promotional Application
----
This project Python with the Flask framework library and SQLAlchemy to organize karate promotionals for Shinkyu Shotokan Karate. Instructors can login, create promotionals, add applications, and generate Judge's Packets, Certificates, and Student Paring sheets. This will cut preparation time for a promotional down from five days to one afternoon.

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

