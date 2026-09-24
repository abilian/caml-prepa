#!/bin/bash

SOURCE=/Users/fermigier/projects/compilers/astero/examples/ocaml/

rsync -avz\
    --exclude .git \
    --exclude .venv \
    --exclude sync.sh \
    --exclude .envrc \
    --exclude .pre-commit-config.yaml \
    --exclude Makefile \
    --exclude .gitignore \
    --delete-after \
     $SOURCE ./
