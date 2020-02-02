#!/bin/bash

SOURCE="`pwd`"
AGENT="blagent"
IMAGE_NAME="tvv${AGENT}"
IMAGE_VERSION=1.0
SECRETS_SERVER="secrets-server"
BLENDERS="/home/tvvdev/Development/archives/blender"
BLENDER_ARCHIVE="blender-2.76b-linux-glibc211-x86_64.tar.bz2"
BLENDER_INST="blender-2.76b-linux-glibc211-x86_64"
MIA_SRC="TVVMia"
MIA_GIT="/home/tvvdev/GIT/${MIA_SRC}"

if [ "$1" == "clean" ]; then
	echo "Pruning containers..."
	docker stop ${SECRETS_SERVER}
	docker container prune -f
	c=`$(docker ps -a -f status=exited -q)`
	if [ "$c" != "" ]; then
		echo "Removing containers..."
		docker rm ${c}
	fi
	di=`$(docker images --filter "dangling=true" -q --no-trunc)`
	if [ "$di" != "" ]; then
		echo "Removing dangling images..."
		docker rmi ${di}
	fi
	echo "Pruning images..."
	docker image prune -f
	for di in `docker image ls -a  | grep '<none>' | awk '{ print $3 }'` `docker image ls -a  | grep "${IMAGE_NAME}" | awk '{ print $3 }'`
	do
		di="${di}"
		echo "Removing images ${di}..."
		docker image rmi -f ${di}
	done
	
	docker container ls
	docker image ls -a
	exit
fi

if [ "$1" == "base" ]; then
	docker image build --file ./Dockerfile --compress --force-rm -t ${IMAGE_NAME}:base --target blagent-base .
fi

if [ "$1" == "requirements" ]; then
	docker image build --file ./Dockerfile --compress --force-rm -t ${IMAGE_NAME}:requirements --target blagent-requirements .
fi

if [ "$1" == "blender" ]; then
	ln -s ${BLENDERS}/${BLENDER_ARCHIVE} blender.tar.bz2
	docker image build --compress --force-rm -t ${IMAGE_NAME}:blender --target blagent-blender --file ./Dockerfile .
fi

if [ "$1" == "source" ]; then
	docker image build --file ./Dockerfile --compress --force-rm -t ${IMAGE_NAME}:source --target blagent-source .
fi

if [ "$1" == "build" ]; then
	di="${IMAGE_NAME}:${IMAGE_VERSION}"
	docker image rmi -f ${di}
#	cp ${BLENDERS}/${BLENDER_ARCHIVE} blender.tar.bz2
#	tar xvf blender.tar.bz2
#	if [ -d "blender" ]; then
#		rm -r blender
#	fi
#	mv ${BLENDER_INST} blender
#	rm blender.tar.bz2
#	cp -r ${MIA_GIT} .
	docker image build --compress --force-rm -t ${di} .
fi


function secret() { # expects: $1 $2 -where $1 == section name, $2 == key name
SECRET_FILE='/tvv/secrets/tvvblender.settings.json'
SECRET_JSON=`jq .${1} $SECRET_FILE`
JSON_VALUE=`echo "$SECRET_JSON" | jq .${2}`
echo $JSON_VALUE
}

if [ "$1" == "run" ]; then
#docker inspect -f "{{ .Config.Env }}" c3f279d17e0a
#$ docker commit --change "ENV DEBUG true" c3f279d17e0a  svendowideit/testimage:version3
#$ docker inspect -f "{{ .Config.Env }}" f5283438590d

	SECTION="TVV_Blagent"
	DEBUG=`secret $SECTION DEBUG`
	SECRET_KEY=`secret $SECTION SECRET_KEY`
	HOST=`secret $SECTION HOST`
	PORT=`secret $SECTION PORT`
	BLENDER_HOME="${BLENDER}"
	#echo "<DEBUG,SECRET_KEY,HOST,PORT>=<$DEBUG,$SECRET_KEY,$HOST,$PORT>"
	ci=`docker container ls -a --filter name=${IMAGE_NAME} | tail -1 | awk '{ print $1 }'`
	if [ "${ci}" != "" ]; then
		docker container rm ${ci}
	fi

#	docker create -t ${IMAGE_NAME}:${IMAGE_VERSION} ${IMAGE_NAME}

#	docker commit \
#		--change "ENV DEBUG ${DEBUG}" \
#		--change "ENV SECRET_KEY ${SECRET_KEY}" \
#		--change "ENV BLAGENT_HOST ${HOST}" \
#		--change "ENV BLAGENT_PORT ${PORT}" \
#		--change "ENV BLENDER_HOME blender" \
#		${IMAGE_NAME}
	
	BLENDER_ENV="--env BLENDER_HOME blender"
	AGENT_FILE="${AGENT}.py"
	BLENDER_ARGS=" -b --verbose 1 --enable-autoexec --python-console --factory-startup -noaudio --python ${AGENT_FILE} "
#	BLENDER_ARGS=" -b -noaudio --python ${AGENT_FILE} "
#	cmd="python3 blagent_injector.py"
	cmd="blender/blender  ${BLENDER_ARGS}"
#	cmd="bin/blender"
	echo "<cmd>=<$cmd>"
	DR="--env "TVV_Blagent_HOST=localhost" --env "TVV_Blagent_PORT=9876" --name ${IMAGE_NAME} ${IMAGE_NAME}:${IMAGE_VERSION} ${cmd}"
#	DR=" --name ${IMAGE_NAME} ${IMAGE_NAME}:${IMAGE_VERSION} ${cmd}"
	echo docker run ${DR}
	docker run ${DR}
fi
