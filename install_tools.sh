#!/bin/sh

# This script will install the underlying command-line tools that are made use
# of by this Sublime package.

set -e
set -x

get() {
	go get -u "$1"
}

# case "$(uname)" in
#     MINGW*)
#         get -ldflags -H=windowsgui github.com/nsf/gocode
#     ;;
#     *)
#         get github.com/nsf/gocode
#     ;;
# esac
get github.com/nsf/gocode

get github.com/godoctor/godoctor

get golang.org/x/tools/cmd/guru

get golang.org/x/tools/cmd/gorename
