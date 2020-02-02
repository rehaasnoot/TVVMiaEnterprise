#!/bin/bash

source venv/bin/activate
source /home/tvvdev/Development/tvvmia/venv/bin/activate

secret() { # expects: $1 $2 -where $1 == section name, $2 == key name
SECRET_FILE='/tvv/secrets/tvvblender.settings.json'
SECRET_JSON=`jq .${1} $SECRET_FILE`
JSON_VALUE=`echo $SECRET_JSON | jq .${2}`
echo $JSON_VALUE | tr -d \"
}

### Define Parameters ###
SECTION_NAME="TVV_Blagent"
REGISTRY_SECTION_NAME="TVV_Blagent_Registry"
HOST=`secret $SECTION_NAME HOST`
PORT=`secret $SECTION_NAME PORT`
USERNAME=`secret $SECTION_NAME USERNAME`
PASSWORD=`secret $SECTION_NAME PASSWORD`
REGISTRY_HOST=`secret $REGISTRY_SECTION_NAME HOST`
REGISTRY_PORT=`secret $REGISTRY_SECTION_NAME PORT`
REGISTRY_USERNAME=`secret $REGISTRY_SECTION_NAME USERNAME`
REGISTRY_PASSWORD=`secret $REGISTRY_SECTION_NAME PASSWORD`

echo "BLAGENT:<HOST,PORT>=<$BLAGENT_HOST,$BLAGENT_PORT>"
#exit

### Process Args ###
while [ "" != "$*" ];
do
#       case word in [ [(] pattern [ | pattern ] ... ) list ;; ] ... esac
	case $1 in
		-h | -help | --help )
			echo "Usage: $PROGNAME <-host hostname> <-port #####> <-username username> <-password password>"
			echo "		<-registry_host host> <-registry_port port> <-registry_username username> <-registry_password password>"
			exit ;;
		-host | -HOST ) shift; if [ "" != "$1" ]; then HOST="$1"; fi ;;
		-port | -PORT ) shift; if [ "" != "$1" ]; then PORT="$1"; fi ;;
		-username | -user | -USERNAME | -USER ) shift; if [ "" != "$1" ]; then USERNAME="$1"; fi ;;
		-password | -PASSWORD | -pass | -PASS ) shift; if [ "" != "$1" ]; then PASSWORD="$1"; fi ;;
		-registry_host | -REGISTRY_HOST ) shift; if [ "" != "$1" ]; then REGISTRY_HOST="$1"; fi ;;
		-registry_port | -REGISTRY_PORT ) shift; if [ "" != "$1" ]; then PORT="$1"; fi ;;
		-registry_username | -registry_user | -REGISTRY_USERNAME | -REGISTRY_USER ) shift; if [ "" != "$1" ]; then REGISTRY_USERNAME="$1"; fi ;;
		-registry_password | -REGISTRY_PASSWORD | -pregistry_pass | -REGISTRY_PASS ) shift; if [ "" != "$1" ]; then REGISTRY_PASSWORD="$1"; fi ;;
	esac
shift
done

export HOST PORT USERNAME PASSWORD
export REGISTRY_HOST REGISTRY_PORT REGISTRY_USERNAME REGISTRY_PASSWORD

FLASK_ENV="development"
export FLASK_ENV
python3 agent.py
