#!/bin/sh

# This script will install the underlying command-line tools that are made use
# of by this Sublime package.

set -e
set -x

get() {
	go get -u "$1"
}

get github.com/nsf/gocode

get github.com/godoctor/godoctor

get golang.org/x/tools/cmd/guru

get golang.org/x/tools/cmd/gorename
