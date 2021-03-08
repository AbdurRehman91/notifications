# Notifications App
This README should:

1-Guide you through getting the Docker container up and running.

2-provide a little explanation as to how it's configured, and

3-provide some basic commands on how to work with

<b>1. Build and run the container</b>
  
  1-Install Docker
  
  2-Download this repository
  
  3-Create a .env file at the same level as this README
  
  4-On the command line, within this directory, do this to build the image and start the container:
  ``` docker-compose build ```
  
  5-If that's successful you can then start it up. This will start up the database and web server,
  and display the Django runserver logs:
  ``` docker-compose up ```
  
 6- Open http://0.0.0.0:8000 in your browser.
