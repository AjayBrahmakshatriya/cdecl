#!/usr/bin/env sh
python cdecl.py < test_set.input > output
diff test_set.output output
