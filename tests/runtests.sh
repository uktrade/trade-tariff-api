#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

# Total seconds to wait until server comes up.
TTF_TEST_INITIAL_DELAY=${TTF_TEST_INITIAL_DELAY:-30}

# Server URL
TTF_TEST_URL="${TTF_TEST_URL:-localhost:8080}"

APIURLLIST="${TTF_TEST_URL}/api/v1/taricdeltas"
APIURLFILE="${TTF_TEST_URL}/api/v1/taricfiles"

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


test "Server comes alive within 30 seconds"
curl --retry ${TTF_TEST_INITIAL_DELAY} --retry-delay 1 --retry-connrefused ${TTF_TEST_URL} -o /dev/null
assert "0" "$?"

test "No API KEY -> expect 403"
out=$(curl -s -w "%{http_code}" -o /dev/null $APIURLLIST)
assert "403" "$out"

test "Invalid date parameter -> expect 400"
out=$(curl -s -i -H "X-API-KEY: abc123" -H "X-Forwarded-For: 1.2.3.4, 127.0.0.1" -w "%{http_code}" -o /dev/null $APIURLLIST/invaliddate)
assert "400" "$out"

test "Non-existent date parameter -> expect 404"
out=$(curl -s -i -H "X-API-KEY: abc123" -H "X-Forwarded-For: 1.2.3.4, 127.0.0.1" -w "%{http_code}" -o /dev/null $APIURLLIST/2000-01-01)
assert "404" "$out"

test "Missing file parameter -> expect 404"
out=$(curl -s -i -H "X-API-KEY: abc123" -H "X-Forwarded-For: 1.2.3.4, 127.0.0.1" -w "%{http_code}" -o /dev/null $APIURLFILE/)
assert "404" "$out"

test "Missing file parameter -> expect 400"
out=$(curl -s -i -H "X-API-KEY: abc123" -H "X-Forwarded-For: 1.2.3.4, 127.0.0.1" -w "%{http_code}" -o /dev/null $APIURLFILE)
assert "400" "$out"

test "Invalid file parameter -> expect 400"
out=$(curl -s -i -H "X-API-KEY: abc123" -H "X-Forwarded-For: 1.2.3.4, 127.0.0.1" -w "%{http_code}" -o /dev/null $APIURLFILE/invalidseq)
assert "400" "$out"

test "Non-existent file parameter -> expect 404"
out=$(curl -s -i -H "X-API-KEY: abc123" -H "X-Forwarded-For: 1.2.3.4, 127.0.0.1" -w "%{http_code}" -o /dev/null $APIURLFILE/150001)
assert "404" "$out"

test "taricdeltas - All correct -> expect 200"
out=$(curl -s -i -H "X-API-KEY: abc123" -H "X-Forwarded-For: 1.2.3.4, 127.0.0.1" -w "%{http_code}" -o /dev/null $APIURLLIST/2019-02-05)
assert "200" "$out"

test "taricfiles - All correct -> expect 200"
out=$(curl -s -i -H "X-API-KEY: abc123" -H "X-Forwarded-For: 1.2.3.4, 127.0.0.1" -w "%{http_code}" -o /dev/null $APIURLFILE/180251)
assert "200" "$out"

test "X-Robots-Tag header is present on responses -> expect noindex, nofollow"
out=$(curl -s -i -I -H "X-API-KEY: abc123" $APIURLFILE/180251 | grep "X-Robots-Tag: noindex, nofollow")
assert "0" "$?"



test "API key not allowed for upload -> expect 403"
out=$(curl -s -i -H "X-API-KEY: abc123" -H "X-Forwarded-For: 1.2.3.4, 127.0.0.1" --form file=@tests/DIT123456.xml -w "%{http_code}" -o /dev/null $APIURLFILE/123456)
assert "403" "$out"

test "No file in POST -> expect 400"
out=$(curl -s -i -H "X-API-KEY: def456" -H "X-Forwarded-For: 1.2.3.4, 127.0.0.1" --form a='a' -w "%{http_code}" -o /dev/null $APIURLFILE/123456)
assert "400" "$out"

test "Incorrect (non-XML) file upload -> expect 400"
out=$(curl -s -i -H "X-API-KEY: def456" -H "X-Forwarded-For: 1.2.3.4, 127.0.0.1" --form file=@tests/invalid.txt -w "%{http_code}" -o /dev/null $APIURLFILE/123456)
assert "400" "$out"

test "Invalid XML file upload -> expect 400"
out=$(curl -s -i -H "X-API-KEY: def456" -H "X-Forwarded-For: 1.2.3.4, 127.0.0.1" --form file=@tests/invalid.txt -w "%{http_code}" -o /dev/null $APIURLFILE/123456)
assert "400" "$out"

test "Missing file sequence upload -> expect 400"
out=$(curl -s -i -H "X-API-KEY: def456" -H "X-Forwarded-For: 1.2.3.4, 127.0.0.1" --form file=@tests/DIT123456.xml -w "%{http_code}" -o /dev/null $APIURLFILE)
assert "400" "$out"

test "Invalid file sequence upload -> expect 400"
out=$(curl -s -i -H "X-API-KEY: def456" -H "X-Forwarded-For: 1.2.3.4, 127.0.0.1" --form file=@tests/DIT123456.xml -w "%{http_code}" -o /dev/null $APIURLFILE/123)
assert "400" "$out"

test "Correct file upload -> expect 200"
out=$(curl -s -i -H "X-API-KEY: def456" -H "X-Forwarded-For: 1.2.3.4, 127.0.0.1" --form file=@tests/DIT123456.xml -w "%{http_code}" -o /dev/null $APIURLFILE/123456)
assert "200" "$out"


test "Invalid modification time on upload -> expect 400"
out=$(curl -s -i -H "X-API-KEY: def456" -H "X-Forwarded-For: 1.2.3.4, 127.0.0.1" --form file=@tests/DIT123456.xml -w "%{http_code}" -o /dev/null $APIURLFILE/123456?modtime=123)
assert "400" "$out"

test "Invalid modification time on upload -> expect 400"
out=$(curl -s -i -H "X-API-KEY: def456" -H "X-Forwarded-For: 1.2.3.4, 127.0.0.1" --form file=@tests/DIT123456.xml -w "%{http_code}" -o /dev/null $APIURLFILE/123456?modtime=2019-01-31-01:02:03.456)
assert "400" "$out"

test "Correct modification time on upload -> expect 200"
out=$(curl -s -i -H "X-API-KEY: def456" -H "X-Forwarded-For: 1.2.3.4, 127.0.0.1" --form file=@tests/DIT123456.xml -w "%{http_code}" -o /dev/null $APIURLFILE/123456?modtime=2019-01-31T01:02:03.456)
assert "200" "$out"


###############################################################
echo
echo "RUN: $tests_run tests"
echo "PASS: $tests_passed tests"

if [ $tests_run != $tests_passed ]; then
    exit 1
fi
