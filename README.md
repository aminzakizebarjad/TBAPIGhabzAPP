# Telemetry Ticket Project
This is a project around thingsboard python REST API module  
 
We will create a Flask project for handling a web UI.  

In this Web UI we first ask for the 


for the project to work you need to create a Ghabz.env file that has a
specific configuration like below, unless no services will be created.  

```
base_url= 
yourThingsBoardUser=
yourThingsBoardPass=
```
Avoid using loopback IP address at base_url.  
If your website has the ssl available never forget to add https:// at the begining.  
There is no need to enter these options in qoute.  
If already there is a proxy set up for your service, then only bring on the ghabz_app service
```
docker compose up -d --build ghabz_app 
```
Otherwize 
```
docker compose up -d --build
```
