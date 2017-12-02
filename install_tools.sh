#!/bin/sh

# This script will install (or update) the underlying command-line tools that
# are made use of by this Sublime package.

set -e
set -x

upsert() {
	go get -u "$1"
}

upsert github.com/godoctor/godoctor
upsert github.com/golang/lint/golint
upsert github.com/nsf/gocode
upsert golang.org/x/tools/cmd/goimports
upsert golang.org/x/tools/cmd/gorename
upsert golang.org/x/tools/cmd/guru
upsert honnef.co/go/tools/cmd/megacheck
