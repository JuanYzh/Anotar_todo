# -*- coding: utf-8 -*-
# Copyright (c) 2023 by wen-Huan.
# Date: 2023-03.01
# Ich und google :)


import nuitka

nuitka.build_one_file(
    "ux_main.py",
    output_dir=".",
    follow_imports=True,
    standalone=True,
    remove_build_dir=True,
    plugin_enable=[],
    plugin_path=[],
)
