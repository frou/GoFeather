#!/bin/sh

# This script will install (or update) the underlying command-line tools that
# are made use of by this Sublime package.

set -e
set -x

upstall() {
	go get -u "$1"
}

upstall github.com/godoctor/godoctor
# TODO(DH): Use the fork instead?
# https://github.com/nsf/gocode/commit/9d1e0378d35b0527c9aef0d17c0913fc38d88b81
# https://github.com/mdempsky/gocode
# "I removed all of the config options" https://github.com/mdempsky/gocode/issues/13#issuecomment-220745687
# But, there is: https://github.com/mdempsky/gocode/blob/9f6c12218c306acb79904362833755c25464b778/gocode.go#L18
upstall github.com/nsf/gocode
upstall golang.org/x/tools/cmd/goimports
upstall golang.org/x/tools/cmd/gorename
upstall golang.org/x/tools/cmd/guru
upstall github.com/golangci/golangci-lint/cmd/golangci-lint
