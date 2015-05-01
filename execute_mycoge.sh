#!/usr/bin/env bash
python initiate.py 2>&1 | tee ./temp/terminal_log.txt
python finalize.py