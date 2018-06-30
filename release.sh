#!/bin/bash

VERSION=${1}

if [ -z "${VERSION}" ];
then
    echo "Usage: ${0} <version>"
    exit 1
fi

git tag --sign v${VERSION} --message="Release v${VERSION}"
git push origin --tags
