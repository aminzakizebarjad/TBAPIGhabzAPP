#set -e

read -p 'give Thingsboard username:' userName
read -sp 'give Thingsboard password:' passWord
user="yourThingsBoardUser = \"${userName}\""
pass="yourThingsBoardPass = \"${passWord}\""
echo $user >> app/userPass.py
echo $pass >> app/userPass.py
DIR=$(pwd)
echo $DIR
cd ..
docker build $DIR -t telapp
docker run -d -p 5000:80 telapp