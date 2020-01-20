#!/bin/bash

VERSION=${1}
DEPLOY=${2}

if [ -z "${VERSION}" ];
then
    echo "Usage: ${0} <version> [--deploy]"
    exit 1
fi

echo "VERSION='${VERSION}'" > plaid2qif/__init__.py
git tag --sign v${VERSION} --message="Release v${VERSION}"
git push origin --tags

if [ ! -z "${DEPLOY}" ];
then
    python3 setup.py sdist bdist_wheel
    twine upload dist/*
fi
