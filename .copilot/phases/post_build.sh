#!/usr/bin/env bash

# Exit early if something goes wrong
set -e

echo "We are downloading copilot"
result=$(python <<EOF
version="1.33.3"
subprocess.run(
    f"wget -q -O copilot-{version} https://ecs-cli-v2-release.s3.amazonaws.com/copilot-linux-v{version} && "
    f"chmod +x ./copilot-{version} && mv copilot-{version} /copilot",
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    shell=True,
    capture_output=True,
)
EOF

echo $result
# Add commands below to run as part of the post_build phase
