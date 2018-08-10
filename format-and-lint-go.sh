#!/bin/sh

# set -x
set -e

SCRIPT_NAME="$(basename "$0")"

exit_with_usage() {
	echo "usage: $SCRIPT_NAME nolint|low|medium|high"
	exit 2
}

test $# = 1 || exit_with_usage

LINT_STRENGTH="$1"

# ------------------------------------------------------------

# See
#     $ golangci-lint linters
# for which linters are available.

case "$LINT_STRENGTH" in
	# TODO(DH): Add this `nolint` capability to the other format-and-lint-* scripts, and update the related Sublime build systems to have a "Format" variant making use of it.
	nolint)
		:
		;;
	low)
		CHOSEN_LINTERS="--disable-all --enable govet,golint"
		;;
	medium)
		CHOSEN_LINTERS="--exclude-use-default=false --disable-all --enable govet,golint,errcheck,ineffassign,interfacer,goconst,gocyclo"
		;;
	high)
		CHOSEN_LINTERS="--exclude-use-default=false --enable-all"
		;;
	*)
		exit_with_usage
		;;
esac

if ls ./*.go >/dev/null 2>&1; then
	# Only try and run goimports if there are files in the wd for the glob to
	# match. This guard is so that the next stage (linting) will still be run
	# in a directory containing no .go files, but whose child directories
	# (recursively) might.
	goimports -w ./*.go
fi

if test -n "$CHOSEN_LINTERS"; then

	# See
	#     $ golangci-lint help run
	# for which general flags are available.

	# See
	#     LintersSettings in https://github.com/golangci/golangci-lint/blob/master/pkg/config/config.go
	# for which linter-specific flags are available.

	# shellcheck disable=SC2086
	golangci-lint run \
		--no-config \
		--out-format tab \
		--print-issued-lines=false \
		--errcheck.check-blank=false \
		--errcheck.check-type-assertions \
		--gocyclo.min-complexity 10 \
		--gofmt.simplify=false \
		$CHOSEN_LINTERS
fi
