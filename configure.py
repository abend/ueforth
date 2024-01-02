#! /usr/bin/env python3
# Copyright 2023 Bradley D. Nelson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
import sys
import subprocess

VERSION = '7.0.7.16'
STABLE_VERSION = '7.0.6.19'
OLD_STABLE_VERSION = '7.0.5.4'

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = SCRIPT_DIR
NINJA_BUILD = os.path.join(ROOT_DIR, 'build.ninja')

CFLAGS_COMMON = [
  '-O2',
  '-I', '$src',
  '-I', '$dst',
]

CFLAGS_MINIMIZE = [
  '-s',
  '-DUEFORTH_MINIMAL',
  '-fno-exceptions',
  '-ffreestanding',
  '-fno-stack-protector',
  '-fomit-frame-pointer',
  '-fno-ident',
  '-ffunction-sections', '-fdata-sections',
  '-fmerge-all-constants',
]

if sys.platform == 'linux':
  CFLAGS_MINIMIZE.append('-Wl,--build-id=none')

CFLAGS = CFLAGS_COMMON + CFLAGS_MINIMIZE + [
  '-std=c++11',
  '-Wall',
  '-Werror',
  '-no-pie',
  '-Wl,--gc-sections',
]

if sys.platform == 'darwin':
  CFLAGS += [
    '-Wl,-dead_strip',
    '-D_GNU_SOURCE',
  ]
elif sys.platform == 'linux':
  CFLAGS += [
    '-s',
    '-Wl,--gc-sections',
    '-no-pie',
    '-Wl,--build-id=none',
  ]

STRIP_ARGS = ['-S']
if sys.platform == 'darwin':
  STRIP_ARGS += ['-x']
elif sys.platform == 'linux':
  STRIP_ARGS += [
    '--strip-unneeded',
    '--remove-section=.note.gnu.gold-version',
    '--remove-section=.comment',
    '--remove-section=.note',
    '--remove-section=.note.gnu.build-id',
    '--remove-section=.note.ABI-tag',
  ]

LIBS = ['-ldl']

WIN_CFLAGS = CFLAGS_COMMON + [
  '-I', '"c:/Program Files (x86)/Microsoft SDKs/Windows/v7.1A/Include"',
  '-I', '"c:/Program Files (x86)/Microsoft Visual Studio/2019/Community/VC/Tools/MSVC/14.28.29333/include"',
  '-I', '"c:/Program Files (x86)/Windows Kits/10/Include/10.0.19041.0/ucrt"',
]

WIN_LIBS = [
  'user32.lib',
]

WIN_LFLAGS32 = [
  '/LIBPATH:"c:/Program Files (x86)/Microsoft SDKs/Windows/v7.1A/Lib"',
  '/LIBPATH:"c:/Program Files (x86)/Microsoft Visual Studio/2019/Community/VC/Tools/MSVC/14.28.29333/lib/x86"',
  '/LIBPATH:"c:/Program Files (x86)/Windows Kits/10/Lib/10.0.19041.0/ucrt/x86"',
] + WIN_LIBS

WIN_LFLAGS64 = [
  '/LIBPATH:"c:/Program Files (x86)/Microsoft SDKs/Windows/v7.1A/Lib/x64"',
  '/LIBPATH:"c:/Program Files (x86)/Microsoft Visual Studio/2019/Community/VC/Tools/MSVC/14.28.29333/lib/x64"',
  '/LIBPATH:"c:/Program Files (x86)/Windows Kits/10/Lib/10.0.19041.0/ucrt/x64"',
] + WIN_LIBS

def Escape(path):
  return path.replace(' ', '\\ ').replace('(', '\\(').replace(')', '\\)')

def LSQ(path):
  return '"' + str(subprocess.check_output('ls ' + Escape(path), shell=True), 'ascii').splitlines()[0] + '"'

PROGFILES = '/mnt/c/Program Files (x86)'
MSVS = PROGFILES + '/Microsoft Visual Studio'
MSKITS = PROGFILES + '/Windows Kits'
WIN_CL32 = LSQ(MSVS + '/*/*/VC/Tools/MSVC/*/bin/Hostx86/x86/cl.exe')
WIN_CL64 = LSQ(MSVS + '/*/*/VC/Tools/MSVC/*/bin/Hostx86/x64/cl.exe')
WIN_LINK32 = LSQ(MSVS + '/*/*/VC/Tools/MSVC/*/bin/Hostx86/x86/link.exe')
WIN_LINK64 = LSQ(MSVS + '/*/*/VC/Tools/MSVC/*/bin/Hostx86/x64/link.exe')
WIN_RC32 = LSQ(MSKITS + '/*/bin/*/x86/rc.exe')
WIN_RC64 = LSQ(MSKITS + '/*/bin/*/x64/rc.exe')

D8 = LSQ('${HOME}/src/v8/v8/out/x64.release/d8')
NODEJS = LSQ('/usr/bin/nodejs')

SRC_DIR = os.path.relpath(ROOT_DIR, os.getcwd())
if SRC_DIR == '.':
  DST_DIR = 'out'
  NINJA_DIR = '.'
else:
  DST_DIR = '.'
  NINJA_DIR = '.'

build_files = []
output = f"""
ninja_required_version = 1.1
src = {SRC_DIR}
dst = {DST_DIR}
ninjadir = {NINJA_DIR}
builddir = $dst
VERSION = {VERSION}
STABLE_VERSION = {STABLE_VERSION}
OLD_STABLE_VERSION = {OLD_STABLE_VERSION}
CFLAGS = {' '.join(CFLAGS)}
STRIP_ARGS = {' '.join(STRIP_ARGS)}
LIBS = {' '.join(LIBS)}
CXX = g++

WIN_CL32 = {WIN_CL32}
WIN_CL64 = {WIN_CL64}
WIN_LINK32 = {WIN_LINK32}
WIN_LINK64 = {WIN_LINK64}
WIN_RC32 = {WIN_RC32}
WIN_RC64 = {WIN_RC64}

D8 = {D8}
NODEJS = {NODEJS}

WIN_CFLAGS = {' '.join(WIN_CFLAGS)}
WIN_LFLAGS32 = {' '.join(WIN_LFLAGS32)}
WIN_LFLAGS64 = {' '.join(WIN_LFLAGS64)}

rule config
  description = CONFIG
  command = $src/configure.py -q

rule revstamp
  description = REVSTAMP
  command = $in $src $out

build $dst/gen/REVISION $dst/gen/REVSHORT: revstamp $src/tools/revstamp.py

rule importation
  description = IMPORTATION $in
  depfile = $out.d
  deps = gcc
  command = $src/tools/importation.py -i $in -o $out -I $dst -I $src $options \
  --depsout $depfile \
  -DVERSION=$VERSION \
  -DSTABLE_VERSION=$STABLE_VERSION \
  -DOLD_STABLE_VERSION=$OLD_STABLE_VERSION \
  -FREVISION=$dst/gen/REVISION \
  -FREVSHORT=$dst/gen/REVSHORT

rule compile
  description = CXX $in
  depfile = $out.d
  deps = gcc
  command = $CXX $CFLAGS $in -o $out $LIBS -MD -MF $depfile && strip $STRIP_ARGS $out

rule compile_sim
  description = CXX_SIM $in
  depfile = $out.d
  deps = gcc
  command = $CXX -DUEFORTH_SIM=1 $CFLAGS $in -o $out $LIBS -MD -MF $depfile && strip $STRIP_ARGS $out

rule compile_win32
  description = WIN_CL32 $in
  deps = msvc
  command = $WIN_CL32 /showIncludes /nologo /c /Fo$out $WIN_CFLAGS $in | $src/tools/posixify.py && touch $out

rule compile_win64
  description = WIN_CL64 $in
  deps = msvc
  command = $WIN_CL64 /showIncludes /nologo /c /Fo$out $WIN_CFLAGS $in | $src/tools/posixify.py && touch $out

rule link_win32
  description = WIN_LINK32 $in
  command = $WIN_LINK32 /nologo /OUT:$out $WIN_LFLAGS32 $in && touch $out && chmod a+x $out

rule link_win64
  description = WIN_LINK64 $in
  command = $WIN_LINK64 /nologo /OUT:$out $WIN_LFLAGS64 $in && touch $out && chmod a+x $out

rule rc_win32
  description = WIN_RC32 $in
  command = $WIN_RC32 /nologo /i $src /fo $out $in && touch $out

rule rc_win64
  description = WIN_RC64 $in
  command = $WIN_RC64 /nologo /i $src /fo $out $in && touch $out

rule run
  description = RUN $in
  command = $in >$out

rule resize
  description = RESIZE $size
  command = convert -resize $size $in $out

rule convert_image
  description = IMAGE_CONVERT $in
  command = convert $in $out

rule zip
  description = ZIP
  command = rm -f $out && cd $base && zip $relout $relin >/dev/null

rule copy
  description = COPY $in
  command = cp $in $out

rule gen_run
  description = GEN_RUN $script
  command = $script $options $infiles >$out

rule oneshot
  description = ONESHOT
  command = echo oneshot

rule forth_test
  description = FORTH_TEST $test
  depfile = $out.d
  deps = gcc
  command = $src/tools/importation.py -i $test -o $out --depsout $depfile --no-out && $interp $forth $test >$out

rule clean
  description = CLEAN
  command = rm -rf $dst/

build clean: clean

rule all_clean
  description = ALL_CLEAN
  command = rm -rf $dst/ && rm build.ninja

build allclean: all_clean

"""


def Importation(target, source, header_mode='cpp', name=None, keep=False, deps=None, implicit=[], options=''):
  global output
  if keep:
    options += ' --keep-first-comment'
  if name:
    options += ' --name ' + name + ' --header ' + header_mode
  implicit = ' '.join(implicit)
  output += f'build {target}: importation {source} | $dst/gen/REVISION $dst/gen/REVSHORT {implicit}\n'
  if options:
    output += f'  options = {options}\n'
  if deps:
    output += f'  depfile = {deps}\n'
  return target


def Esp32Optional(main_name, main_source, parts):
  parts = []
  for name, source in parts:
    parts.append(Importation('$dst/gen/esp32_' + name + '.h',
                             source, name=name.replace('-', '_') + '_source'))
  return Importation('$dst/esp32/ESP32forth/optional/' + main_name + '.h',
                     main_source,
                     keep=True,
                     deps='$dst/gen/esp32_optional_' + main_name + '.h.d',
                     implicit=parts)


def Simple(op, target, source, implicit=[]):
  global output
  implicit = ' '.join(implicit)
  output += f'build {target}: {op} {source} | {implicit}\n'
  return target


def Compile(target, source, implicit=[]):
  return Simple('compile', target, source, implicit)


def CompileSim(target, source, implicit=[]):
  return Simple('compile_sim', target, source, implicit)


def CompileW32(target, source, implicit=[]):
  return Simple('compile_win32', target, source, implicit)


def CompileW64(target, source, implicit=[]):
  return Simple('compile_win64', target, source, implicit)


def LinkW32(target, source, implicit=[]):
  return Simple('link_win32', target, source, implicit)


def LinkW64(target, source, implicit=[]):
  return Simple('link_win64', target, source, implicit)


def ResizeImage(target, source, size, implicit=[]):
  global output
  Simple('resize', target, source, implicit)
  output += f'  size={size}\n'
  return target


def ConvertImage(target, source, implicit=[]):
  return Simple('convert_image', target, source, implicit)


def CompileResource32(target, source, implicit=[]):
  return Simple('rc_win32', target, source, implicit)


def CompileResource64(target, source, implicit=[]):
  return Simple('rc_win64', target, source, implicit)


def Run(target, source, implicit=[]):
  return Simple('run', target, source, implicit)


def Zip(target, sources, base):
  global output
  ret = Simple('zip', target, ' '.join(sources))
  relin = ' '.join([os.path.relpath(i, base) for i in sources])
  relout = os.path.relpath(target, base)
  output += f'  base = {base}\n'
  output += f'  relout = {relout}\n'
  output += f'  relin = {relin}\n'
  return ret


def Alias(target, source):
  global output
  output += f'build {target}: phony {source}\n'
  return target


def Copy(target, source):
  global output
  output += f'build {target}: copy {source}\n'
  return target


def GenRun(target, script, options, sources):
  sources = ' '.join(sources)
  global output
  output += f'build {target}: gen_run {script} {sources}\n'
  output += f'  options = {options}\n'
  output += f'  script = {script}\n'
  output += f'  infiles = {sources}\n'
  return target


def OneShot(target, command, source, pool=None):
  global output
  output += f'build {target}: oneshot {source}\n'
  output += f'  command = {command}\n'
  if pool:
    output += f'  pool = {pool}\n'
  return target


def ForthTest(target, forth, test, interp='', pool=None):
  global output
  output += f'build {target}: forth_test {forth} {test}\n'
  output += f'  forth = {forth}\n'
  output += f'  test = {test}\n'
  output += f'  interp = {interp}\n'
  if pool:
    output += f'  pool = {pool}\n'
  return target


def Default(target):
  global output
  output += f'default {target}\n'
  return target


def Include(path):
  build_files.append(os.path.join('$src', path, 'BUILD'))
  path = os.path.join(ROOT_DIR, path, 'BUILD')
  data = open(path).read()
  exec(data)


def Main():
  parser = argparse.ArgumentParser(
    prog='configure',
    description='Generate ninja.build')
  parser.add_argument('-q', '--quiet', action='store_true')
  args = parser.parse_args()
  Include('.')
  with open('build.ninja', 'w') as fh:
    fh.write(output)
    fh.write(f'build $ninjadir/build.ninja: config $src/configure.py ' + ' '.join(build_files) + '\n')
  if not args.quiet:
    print('TO BUILD RUN: ninja')


if __name__ == '__main__':
  Main()
