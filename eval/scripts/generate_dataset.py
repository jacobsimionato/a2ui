# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Compiles and exports the complete 30-case synthetic research evaluation dataset."""

import sys
from pathlib import Path
import yaml

sys.path.insert(0, 'eval/scripts')
from cases_part1 import CASES_PART_1
from cases_part2 import CASES_PART_2
from cases_part3 import CASES_PART_3

all_cases = CASES_PART_1 + CASES_PART_2 + CASES_PART_3
assert len(all_cases) == 30, f"Expected 30 cases, found {len(all_cases)}"

class IndentedDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)

def str_presenter(dumper, data):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)

IndentedDumper.add_representer(str, str_presenter)

output_path = Path("eval/datasets/research_use_cases.yaml")
with open(output_path, "w", encoding="utf-8") as f:
    yaml.dump(all_cases, f, Dumper=IndentedDumper, sort_keys=False, width=1000)

print(f"Successfully exported {len(all_cases)} cases to {output_path} ({output_path.stat().st_size} bytes)")
