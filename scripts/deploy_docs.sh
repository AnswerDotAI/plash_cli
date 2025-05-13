#!/usr/bin/env bash
rm -rf docs_site/_proc
nbdev_docs
cp -r _docs docs_site/
plash_deploy --path docs_site