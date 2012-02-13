#!/usr/bin/env bash
pycodestyle --max-line-length=120 parse_toys tests && \
    nosetests --nocapture --with-coverage --cover-erase --cover-html --cover-html-dir=htmlcov --cover-package=parse_toys --with-doctest