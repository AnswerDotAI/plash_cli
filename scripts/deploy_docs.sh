#!/usr/bin/env bash
rm -rf _proc
rm -rf docs_site/_docs
nbdev_docs
cp -r _docs docs_site/
plash_deploy --path docs_site