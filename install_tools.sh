#!/bin/sh

# This script will install (or update) the underlying command-line tools that
# are made use of by this Sublime package.

# TODO: Port this to Python and have it be callable from the Command Palette

set -e
set -x

upstall() {
	go get -u "$@"
}

upstall github.com/mdempsky/gocode
upstall github.com/godoctor/godoctor
upstall golang.org/x/tools/cmd/goimports
upstall golang.org/x/tools/cmd/gorename
upstall golang.org/x/tools/cmd/guru
upstall github.com/golangci/golangci-lint/cmd/golangci-lint
upstall github.com/zmb3/gogetdoc
