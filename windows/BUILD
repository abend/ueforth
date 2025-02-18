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

if not WINDOWS_ENABLED:
  Return()

Alias('windows', 'win32 win64')
if not FAST:
  Default('windows')

# Create boot.
Importation('$dst/gen/windows_boot.h', '$src/windows/windows_boot.fs',
            header_mode='win', name='boot')
Importation('$dst/gen/windows_boot_extra.h', '$src/windows/windows_boot_extra.fs',
            header_mode='win', name='boot_extra')

# Compile Win32.
Alias('win32', ' '.join([
  ForthTest('$dst/tests/win32_all_tests.out',
            '$dst/windows/uEf32.exe', '$src/common/all_tests.fs',
            interp='wineconsole --backend=curses'),
]))
CompileW32('$dst/windows/uEf32.obj', '$src/windows/main.c',
           implicit=['$dst/gen/windows_boot.h',
                     '$dst/gen/windows_boot_extra.h'])
LinkW32('$dst/windows/uEf32.exe',
        ' '.join(['$dst/windows/uEf32.obj',
                  '$dst/resources/ueforth_res32.res']))

# Compile Win64.
Alias('win64', ' '.join([
  ForthTest('$dst/tests/win64_all_tests.out',
            '$dst/windows/uEf64.exe', '$src/common/all_tests.fs',
            interp='wineconsole --backend=curses'),
]))
CompileW64('$dst/windows/uEf64.obj', '$src/windows/main.c',
           implicit=['$dst/gen/windows_boot.h',
                     '$dst/gen/windows_boot_extra.h'])
LinkW64('$dst/windows/uEf64.exe',
        ' '.join(['$dst/windows/uEf64.obj',
                  '$dst/resources/ueforth_res64.res']))

# Create icon.
Copy('$dst/resources/eforth.ico', 'images/eforth.ico')
CompileResource32('$dst/resources/ueforth_res32.res', '$src/windows/ueforth.rc',
                  implicit=['$dst/resources/eforth.ico'])
CompileResource64('$dst/resources/ueforth_res64.res', '$src/windows/ueforth.rc',
                  implicit=['$dst/resources/eforth.ico'])

OneShot('win-install',
        ' '.join([
          '$dst/windows/uEf64.exe',
        ]),
        'sudo cp $dst/windows/uEf64.exe ~/Desktop',
        pool='console')
