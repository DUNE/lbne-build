#!/usr/bin/env python
# encoding: utf-8

import os
import sys

top = '.'
out = 'tmp'

def options(opt):
    opt.load('orchlib', tooldir='.')

def configure(cfg):
    cfg.load('orchlib', tooldir='.')

def build(bld):
    bld.load('orchlib', tooldir='.')
