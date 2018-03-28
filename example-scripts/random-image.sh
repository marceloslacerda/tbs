#!/usr/bin/env sh
json_output=True

service="https://picsum.photos/200/300/?image=935"

data=$(wget "$service" -O - | base64)
echo '{"type": "image", "content": "'"$data"'"}'