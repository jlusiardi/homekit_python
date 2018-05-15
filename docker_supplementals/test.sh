#!/bin/bash

RECIPIENT=$1
RESULTDIR=`mktemp -d`
ID=`date | md5sum | sed 's/ -//'`
NETWORK=homekit_net_${ID}
CONTAINER=homekit_container_${ID}


function perform_test {
	COMMAND="$1"
	TESTNAME="$2"
	docker exec -ti ${CONTAINER} bash -c "PYTHONPATH=. python3 homekit/${COMMAND}" > ${RESULTDIR}/${TESTNAME}.result
	RESULT=$?
	if (( ${RESULT} != 0 )); then
        	echo "${TESTNAME} failed (${RESULT})" >> ${RESULTDIR}/status
	else
        	echo "${TESTNAME} worked (${RESULT})" >> ${RESULTDIR}/status
	fi
}

#	setup network
docker network create ${NETWORK} --subnet 192.168.178.0/24 > /dev/null

#	start homekit accessory
docker run --name ${CONTAINER} -d --ip 192.168.178.21 --network ${NETWORK} homekit_python:latest bash -c "cd /homekit_python; git pull; PYTHONPATH=. python3 demoserver.py" > /dev/null

sleep 5s

# 	run discover test
COMMAND="discover.py"
TESTNAME="discover_1"
perform_test "${COMMAND}" "${TESTNAME}"

#	run pair test
COMMAND="pair.py -d 12:34:00:00:00:04 -p 031-45-154 -f demoserver.json"
TESTNAME="pair_1"
perform_test "${COMMAND}" "${TESTNAME}"

COMMAND="get_accessories.py -f demoserver.json"
TESTNAME="get_accessories_1"
perform_test "${COMMAND}" "${TESTNAME}"


#	remove container but back up logs
docker logs ${CONTAINER} &> ${RESULTDIR}/accessory.logs
docker rm -f ${CONTAINER} > /dev/null

#       remove network
docker network rm ${NETWORK} > /dev/null

cd ${RESULTDIR}
ls -hal
rm /tmp/homekit_test.zip
zip /tmp/homekit_test.zip *
mpack -s "Homekit Test" -d ${RESULTDIR}/status /tmp/homekit_test.zip ${RECIPIENT}
