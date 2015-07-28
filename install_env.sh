#!/bin/bash
APPNAME="dingo"

[ "$1" ] && VENVNAME="$1"
if [ -z $VENVNAME ]; then
  VENVNAME="${APPNAME}_env"
fi

if [ -z "$RAGNAROK" ]; then
  APP_DIR="${HOME}/${APPNAME}"
  PIP_WHEEL_DIR=/tmp/pip_wheel
  sudo npm -g install grunt-cli ycssmin
  sudo chown vagrant:vagrant /home/vagrant/.npm/ -R
else
  APP_DIR="${CODE_ROOT}/${APPNAME}"
  PIP_WHEEL_DIR="${ENV_ROOT}/wheels"
  npm -g install grunt-cli ycssmin
fi

VENV_PATH=${WORKON_HOME}/${VENVNAME}
DIST_URL=https://distmebatman:omgrawr@ext-dist.keep.com/
PIP_REQS_FILE="${APP_DIR}/pip_requirements.txt"
PIP_BUILD_REQS_FILE="${APP_DIR}/pip_build_requirements.txt"

test -d ${PIP_WHEEL_DIR} || mkdir -p $PIP_WHEEL_DIR
test -d ${VENV_PATH} || init_env ${APPNAME} ${VENVNAME}

# Install Python (Must be on vpn)
. ${VENV_PATH}/bin/activate
${VENV_PATH}/bin/pip install --download ${PIP_WHEEL_DIR} --find-links=${DIST_URL} -r ${PIP_REQS_FILE}
${VENV_PATH}/bin/pip wheel --find-links=${PIP_WHEEL_DIR} --wheel-dir=${PIP_WHEEL_DIR} -r ${PIP_REQS_FILE}
${VENV_PATH}/bin/pip install --use-wheel --find-links=${PIP_WHEEL_DIR} -r ${PIP_REQS_FILE}
