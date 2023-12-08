#!/bin/bash

set -eux

rm -rf ~/.brainstorm
rm -rf /tmp/brainstorm_db
rm -rf /tmp/brainstorm_temp

rsync -rav ./.brainstorm ~/
rsync -rav ./brainstorm_db /tmp/
