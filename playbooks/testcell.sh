#!/bin/bash
set -e
set -x
: Running postcreate script for ${VIRTLAB_NAME}
ansible-playbook -i ${VIRTLAB_SCRIPTDIR}/inventory.sh ${VIRTLAB_LOCAL_PLAYBOOKS} ${VIRTLAB_PLAYBOOK}
ssh ${VIRTLAB_TESTHOST} run-openafs-robotest.sh ${VIRTLAB_TESTSUITE}
