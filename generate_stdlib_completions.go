package main

import (
	"bufio"
	"bytes"
	"fmt"
	"log"
	"os"
	"os/exec"
	"regexp"
	"strings"
)

// http://docs.sublimetext.info/en/latest/extensibility/completions.html
// http://docs.sublimetext.info/en/latest/reference/completions.html

func main() {
	if err := run(); err != nil {
		log.Fatal(err)
	}
}

var (
	reConstVar = regexp.MustCompile(`pkg (\S+)( \(\w+-\w+-\w+\))?, (const|var) ([\pL_][\pL_\p{Nd}]+) ([^=]+)`)
	reFunc     = regexp.MustCompile(`pkg (\S+)( \(\w+-\w+-\w+\))?, (func) ([\pL_][\pL_\p{Nd}]+)(.+)`)
	reType     = regexp.MustCompile(`pkg (\S+)( \(\w+-\w+-\w+\))?, (type) ([\pL_][\pL_\p{Nd}]+)`)
)

func run() error {

	apiCmd := exec.Command("go", "tool", "api")
	apiOutput, err := apiCmd.Output()
	if err != nil {
		return err
	}

	outFile, err := os.Create("stdlib.sublime-completions")
	if err != nil {
		return err
	}
	defer outFile.Close()

	// TODO(DH): Build up JSON property by defining a Go struct.
	fmt.Fprint(outFile, `{"scope":"source.go","completions":[`)
	defer fmt.Fprint(outFile, `]}`)

	scanner := bufio.NewScanner(bytes.NewReader(apiOutput))
	for scanner.Scan() {
		line := scanner.Text()
		if submatches := reConstVar.FindStringSubmatch(line); submatches != nil {
			pkg := lastComponentOfImportPath(submatches[1])
			kind := submatches[3]
			identifier := submatches[4]
			// typ := submatches[5]

			fmt.Fprintf(outFile, `{"trigger":"%s %s\t%s", "contents":"%s.%s"},`,
				pkg, identifier, kind,
				pkg, identifier)
		} else if submatches := reFunc.FindStringSubmatch(line); submatches != nil {
			pkg := lastComponentOfImportPath(submatches[1])
			kind := submatches[3]
			identifier := submatches[4]
			// sigHint := submatches[5]

			fmt.Fprintf(outFile, `{"trigger":"%s %s\t%s", "contents":"%s.%s"},`,
				pkg, identifier, kind,
				pkg, identifier)
		} else if submatches := reType.FindStringSubmatch(line); submatches != nil {
			pkg := lastComponentOfImportPath(submatches[1])
			kind := submatches[3]
			identifier := submatches[4]

			fmt.Fprintf(outFile, `{"trigger":"%s %s\t%s", "contents":"%s.%s"},`,
				pkg, identifier, kind,
				pkg, identifier)
		}
	}
	return scanner.Err()
}

func lastComponentOfImportPath(path string) string {
	components := strings.Split(path, "/")
	return components[len(components)-1]
}
