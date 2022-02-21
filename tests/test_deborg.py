"""
Tests for the command line utility deborg accessed via deborg.__main__.py.
"""

from __future__ import annotations

import pytest


def test_non_existing_orgfile_raises_error(script_runner):
    ret = script_runner.run('deborg', '--version')
    assert ret.success
    assert ret.stderr == ''
