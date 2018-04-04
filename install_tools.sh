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

# gometalinter does something complex where it vendors the source code of all
# the linter commands it knows about, and itself provides a runtime flag to
# take resposibility for building and installing them.
#
# The following should perform a smooth install/update of gometalinter and the
# linter commands it vendors:
GML="github.com/alecthomas/gometalinter"
rm -rf "$GOPATH/src/$GML" # Possibly contains work the user cares about...? TODO(DH): Pass -I flag to rm?
upstall "$GML"
gometalinter --install
