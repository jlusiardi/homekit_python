#!/bin/bash

RECIPIENT=$1
BRANCH=${2:-master}
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
        	echo "--> ${TESTNAME} failed (${RESULT})" >> ${RESULTDIR}/status
	else
        	echo "--> ${TESTNAME} worked (${RESULT})" >> ${RESULTDIR}/status
	fi
	cat ${RESULTDIR}/${TESTNAME}.result >> ${RESULTDIR}/status
	echo "==================================================" >> ${RESULTDIR}/status
}

#	setup network
docker network create ${NETWORK} --subnet 192.168.178.0/24 > /dev/null

#	start homekit accessory and wait sometime to complete git pull
docker run --name ${CONTAINER} -d --ip 192.168.178.21 --network ${NETWORK} homekit_python:latest bash -c "cd /homekit_python; git checkout ${BRANCH}; git pull; PYTHONPATH=. python3 demoserver.py" > /dev/null
sleep 5s

################################ run tests ################################

# 	run discover test
COMMAND="discover.py"
TESTNAME="discover_1"
perform_test "${COMMAND}" "${TESTNAME}"

#	run pair test
COMMAND="pair.py -d 12:34:00:00:00:04 -p 031-45-154 -f demoserver.json"
TESTNAME="pair_1"
perform_test "${COMMAND}" "${TESTNAME}"

#   get accessories
COMMAND="get_accessories.py -f demoserver.json"
TESTNAME="get_accessories_1"
perform_test "${COMMAND}" "${TESTNAME}"

#   get characteristic
COMMAND="get_characteristic.py -f demoserver.json -c 1.10"
TESTNAME="get_characteristic_1"
perform_test "${COMMAND}" "${TESTNAME}"

#   put characteristic
COMMAND="put_characteristic.py -f demoserver.json -c 1.10 -v off"
TESTNAME="put_characteristic_1"
perform_test "${COMMAND}" "${TESTNAME}"

#   get characteristic
COMMAND="get_characteristic.py -f demoserver.json -c 1.10"
TESTNAME="get_characteristic_2"
perform_test "${COMMAND}" "${TESTNAME}"

#   put characteristic
COMMAND="put_characteristic.py -f demoserver.json -c 1.10 -v on"
TESTNAME="put_characteristic_2"
perform_test "${COMMAND}" "${TESTNAME}"

#   get characteristic
COMMAND="get_characteristic.py -f demoserver.json -c 1.10"
TESTNAME="get_characteristic_3"
perform_test "${COMMAND}" "${TESTNAME}"

#   unpair
COMMAND="unpair.py -f demoserver.json -d"
TESTNAME="unpair_3"
perform_test "${COMMAND}" "${TESTNAME}"



################################ cleanup and mail result ################################

#	remove container but back up logs
docker logs ${CONTAINER} &> ${RESULTDIR}/accessory.logs
docker rm -f ${CONTAINER} > /dev/null

#       remove network
docker network rm ${NETWORK} > /dev/null

cd ${RESULTDIR}
rm /tmp/homekit_test.zip
zip /tmp/homekit_test.zip * > /dev/null
mpack -s "Homekit Test for ${BRANCH}" -d ${RESULTDIR}/status /tmp/homekit_test.zip ${RECIPIENT}
rm -rf ${RESULTDIR}
