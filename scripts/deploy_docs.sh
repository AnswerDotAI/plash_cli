#!/usr/bin/env bash
set -e

rm -rf _proc _docs
rm -rf docs_site/_docs
nbdev_docs
cp -r _docs docs_site/
plash_deploy --path docs_site ${1:+--name "$1"}
plash_logs --tail ${1:+--name "$1"}