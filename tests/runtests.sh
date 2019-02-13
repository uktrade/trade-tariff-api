#!/bin/bash

typeset -i tests_run=0
typeset -i tests_passed=0

function test {
    this="$1";
}

trap 'printf "$0: exit code $? on line $LINENO\nFAIL: $this\n"; exit 1' ERR

function assert {
    let tests_run+=1
    [ "$1" = "$2" ] && {
        let tests_passed+=1
        printf "\n$tests_run    PASS: $this\n";
        printf "    '$1' == '$2'\n";
        return;
    }
    printf "\n$tests_run    FAIL: $this\n"
    printf "    '$1' != '$2'\n";
    #exit 1
}

###############################################################

URL=http://localhost:8080
APIURLLIST=http://localhost:8080/api/v1/taricdeltas
APIURLFILE=http://localhost:8080/api/v1/taricfiles

test "No API KEY or whitelisted IP -> expect 403"
out=$(curl -s -w "%{http_code}" -o /dev/null $APIURLLIST)
assert "403" "$out"


test "API KEY but no whitelisted IP -> expect 403"
out=$(curl -s -i -H "X-API-KEY: abc123" -w "%{http_code}" -o /dev/null $APIURLLIST)
assert "403" "$out"


test "Invalid date parameter -> expect 400"
out=$(curl -s -i -H "X-API-KEY: abc123" -w "%{http_code}" -o /dev/null $APIURLLIST/invaliddate)
assert "400" "$out"

test "Non-existent date parameter -> expect 404"
out=$(curl -s -i -H "X-API-KEY: abc123" -w "%{http_code}" -o /dev/null $APIURLLIST/2000-01-01)
assert "404" "$out"

test "Missing file parameter -> expect 400"
out=$(curl -s -i -H "X-API-KEY: abc123" -w "%{http_code}" -o /dev/null $APIURLFILE)
assert "400" "$out"

test "Invalid file parameter -> expect 400"
out=$(curl -s -i -H "X-API-KEY: abc123" -w "%{http_code}" -o /dev/null $APIURLFILE/invalidseq)
assert "400" "$out"

test "Non-existent file parameter -> expect 404"
out=$(curl -s -i -H "X-API-KEY: abc123" -w "%{http_code}" -o /dev/null $APIURLFILE/15001)
assert "404" "$out"



test "Example of POST XML"

# Post xml (from hello.xml file) on /hello
out=$(cat test/hello.xml | curl -s -H "Content-Type: text/xml" -d @- \
  -X POST $URL/hello)
assert "Hello World" "$out"


###############################################################
echo
echo "RUN: $tests_run tests"
echo "PASS: $tests_passed tests"