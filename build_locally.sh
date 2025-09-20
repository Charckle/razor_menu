USERNAME=charckle
VERSION=$(cat VERSION)
IMAGE=razor_menu

docker build -f Dockerfile-alpine -t $USERNAME/$IMAGE:$VERSION-alpine .
