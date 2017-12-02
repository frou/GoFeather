#!/bin/sh

# This script will install (or update) the underlying command-line tools that
# are made use of by this Sublime package.

set -e
set -x

upsert() {
	go get -u "$1"
}

upsert github.com/golang/lint/golint

upsert golang.org/x/tools/cmd/goimports

upsert honnef.co/go/tools/cmd/megacheck

upsert github.com/nsf/gocode

upsert github.com/godoctor/godoctor

upsert golang.org/x/tools/cmd/guru

upsert golang.org/x/tools/cmd/gorename
