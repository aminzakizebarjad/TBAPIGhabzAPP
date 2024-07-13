#set -e
#read -p 'give Thingsboard username:' userName
#read -sp 'give Thingsboard password:' passWord
#user=""$'\n'"yourThingsBoardUser = \"${userName}\""
#pass="yourThingsBoardPass = \"${passWord}\""
#echo $user >> app/userPass.py
#echo $pass >> app/userPass.py

docker compose up -d --build