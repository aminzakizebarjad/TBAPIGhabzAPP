# AbinegarProject - Ghabz/AI Dahsboard
## Summary
This project is a fork of another project which was an IOT Dashboard.
We added new AI and Deep Learning capabilities to this dashboard for further use.
The Main project can be found [here](https://github.com/aminzakizebarjad/TBAPIGhabzAPP)

## Instructions
The needed instruction to run the dashboard is explained in this section

### python venv
Create a python virtual environment then install the needed libraries inside requirement.txt file

### make .env file
To make use of the data, you need to have the credentials.
Make a .env file at the root of the project repository and writ the following inside it:
```
base_url= your_url #https://tb1.thingsware.cloud
yourThingsBoardUser= your_username
yourThingsBoardPass= your_password
```

### Run 
To run the project do not use the run.py or server.py 
Instead head to app folder and run the **main.py**

Example, If you are at the root of repositiry: 
```
python app/main.py
```
Then you can go to the default address bellow ( if not changed ) to access the dashboard:
```
http://127.0.0.1:5000/ghabz
```
