set -e
DIR = pwd
cd ..
docker build $DIR -t telapp
docker run -d -p 5000:80 telapp
