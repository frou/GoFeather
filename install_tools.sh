#!/bin/sh

# This script will install (or update) the underlying command-line tools that
# are made use of by this Sublime package.

set -e
set -x

upstall() {
	go get -u "$1"
}

upstall github.com/godoctor/godoctor
upstall github.com/nsf/gocode
upstall golang.org/x/tools/cmd/goimports
upstall golang.org/x/tools/cmd/gorename
upstall golang.org/x/tools/cmd/guru
