// Copyright 2025 Seth Ladygo
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
 * ESP32forth JSON v{{VERSION}}
 * Revision: {{REVISION}}
 */

// You will need to install these libraries from the Library Manager:
//   ArduinoJson

#include <ArduinoJson.h>

#define jdoc0 ((JsonDocument *) a0)

static void jsonDeserialize(JsonDocument *doc, const char *json) {
  DeserializationError error = deserializeJson(*doc, json);

  if (error) {
    // TODO throw?
    Serial.print(F("deserializeJson() failed: "));
    Serial.println(error.f_str());
    return;
  }
}

static void setNumberJsonAttribute(JsonDocument *doc, const char *name, cell_t value) {
  int32_t v = (int32_t)value;
  (*doc)[name] = v;
}

static void setStringJsonAttribute(JsonDocument *doc, const char *name, const char *value) {
  (*doc)[name] = value;
}

static cell_t getNumberJsonAttribute(JsonDocument *doc, const char *name) {
  return (*doc)[name];
}

static cell_t getStringJsonAttribute(JsonDocument *doc, const char *name) {
  const char *value = (*doc)[name];
  return (cell_t)value;
}

static cell_t jsonContains(JsonDocument *doc, const char *name) {
  return (*doc).containsKey(name) ? -1 : 0;
}

static void jsonRemove(JsonDocument *doc, const char *name) {
  (*doc).remove(name);
}

#define OPTIONAL_JSON_VOCABULARY V(json)
#define OPTIONAL_JSON_SUPPORT                                   \
  XV(json, "json-create", CREATE_JSON, PUSH new JsonDocument()) \
  XV(json, "json-delete", JSON_DELETE, delete jdoc0; DROP) \
  XV(json, "json-is-null", JSON_IS_NULL, n0 = jdoc0->isNull() ? -1 : 0) \
  XV(json, "json-size", JSON_SIZE, n0 = jdoc0->size()) \
  XV(json, "json-nesting", JSON_NESTING, n0 = jdoc0->nesting()) \
  XV(json, "json-deserialize", JSON_DESERIALIZE, jsonDeserialize(jdoc0, c1); NIPn(2);) \
  XV(json, "json-set-number", JSON_SET_STRING, setNumberJsonAttribute(jdoc0, c1, n2); DROPn(3);) \
  XV(json, "json-set-string", JSON_SET_NUMBER, setStringJsonAttribute(jdoc0, c1, c2); DROPn(3);) \
  XV(json, "json-get-number", JSON_GET_NUMBER, n0 = getNumberJsonAttribute(jdoc0, c1); NIP;) \
  XV(json, "json-get-string", JSON_GET_STRING, n0 = getStringJsonAttribute(jdoc0, c1); NIP;) \
  XV(json, "json-contains", JSON_CONTAINS, n0 = jsonContains(jdoc0, c1); NIPn(1);) \
  XV(json, "json-remove", JSON_REMOVE, jsonRemove(jdoc0, c1); NIPn(2);) \
  XV(json, "json-clear", JSON_CLEAR, jdoc0->clear(); NIP)
