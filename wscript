#!/usr/bin/env python
# encoding: utf-8

top = '.'
out = 'tmp'

import os
mydir = os.path.realpath('.')

import sys
sys.path.insert(0,os.path.join(mydir,'worch'))

# fixme, add git clone worch code here

def options(opt):
    opt.load('orchlib', tooldir='.')

def configure(cfg):
    cfg.load('orchlib', tooldir='.')

def build(bld):
    bld.load('orchlib', tooldir='.')
