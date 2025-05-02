// Copyright 2025 Bradley D. Nelson
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/*
 * ESP32forth LittleFS v{{VERSION}}
 * Revision: {{REVISION}}
 */

/*
  /home/alx/.arduino15/packages/esp32/tools/esptool_py/4.9.dev3/esptool
  --chip esp32
  --port /dev/ttyACM0
  --baud 921600
  --before default_reset
  --after hard_reset write_flash
  -z
  --flash_mode dio
  --flash_freq 80m
  --flash_size detect 2686976
  /tmp/tmp-3773584-p2pqnbQh6eFu-.littlefs.bin
*/

#include "LittleFS.h"


#define FORMAT_LITTLEFS_IF_FAILED false

void listDir(fs::FS &fs, const char *dirname, uint8_t levels) {
  Serial.printf("Listing directory: %s\r\n", dirname);

  File root = fs.open(dirname);
  if (!root) {
    Serial.println("- failed to open directory");
    return;
  }
  if (!root.isDirectory()) {
    Serial.println(" - not a directory");
    return;
  }

  File file = root.openNextFile();
  while (file) {
    if (file.isDirectory()) {
      Serial.print("  DIR : ");
      Serial.println(file.name());
      if (levels) {
        listDir(fs, file.path(), levels - 1);
      }
    } else {
      Serial.print("  FILE: ");
      Serial.print(file.name());
      Serial.print("\tSIZE: ");
      Serial.println(file.size());
    }
    file = root.openNextFile();
  }
}

void testList() {
  // Serial.begin(115200);

  if (!LittleFS.begin(FORMAT_LITTLEFS_IF_FAILED)) {
    Serial.println("LittleFS Mount Failed");
    return;
  }

  Serial.println("SPIFFS-like write file to new path and delete it w/folders");
  listDir(LittleFS, "/", 3);
}

void printPartitions() {
  const esp_partition_t *partitions;
  size_t num_partitions;
  esp_partition_iterator_t iterator = esp_partition_find(ESP_PARTITION_TYPE_DATA,
                                                         ESP_PARTITION_SUBTYPE_ANY,
                                                         NULL);

  while (iterator != nullptr) {
    partitions = esp_partition_get(iterator);
    Serial.printf("Name: %s, Type: %d, Subtype: %d, Offset: 0x%06x, Size: %u\n",
                  partitions->label,
                  partitions->type,
                  partitions->subtype,
                  partitions->address,
                  partitions->size);
    iterator = esp_partition_next(iterator);
  }
  esp_partition_iterator_release(iterator);
}

#define OPTIONAL_LITTLEFS_VOCABULARY V(LittleFS)
#define OPTIONAL_LITTLEFS_SUPPORT \
  XV(internals, "littlefs-source", LITTLEFS_SOURCE,           \
     PUSH littlefs_source; PUSH sizeof(littlefs_source) - 1)  \
  XV(LittleFS, "LittleFS.begin", LITTLEFS_BEGIN, PUSH LittleFS.begin()) \
  XV(LittleFS, "LittleFS.test", LITTLEFS_TEST, testList()) \
  XV(LittleFS, "LittleFS.pp", LITTLEFS_PP, printPartitions()) \
  XV(LittleFS, "LittleFS.format", LITTLEFS_FORMAT, PUSH LittleFS.format()) \
  XV(LittleFS, "LittleFS.totalBytes", LITTLEFS_TOTAL_BYTES, PUSH LittleFS.totalBytes()) \
  XV(LittleFS, "LittleFS.usedBytes", LITTLEFS_USED_BYTES, PUSH LittleFS.usedBytes())

#include "gen/esp32_littlefs.h"
