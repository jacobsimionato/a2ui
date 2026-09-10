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

"""Merges all 6 subagent batch YAML files into research_use_cases.yaml."""

from pathlib import Path
import yaml

class IndentedDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)

def str_presenter(dumper, data):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)

IndentedDumper.add_representer(str, str_presenter)

all_cases = []
for batch_idx in range(1, 7):
    batch_file = Path(f"temp_docs/batch_{batch_idx}.yaml")
    if not batch_file.exists():
        print(f"Batch file {batch_file} not found yet.")
        continue
    with open(batch_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    print(f"Loaded {len(data)} cases from {batch_file}")
    all_cases.extend(data)

print(f"Total cases collected: {len(all_cases)}")
if len(all_cases) == 30:
    out_path = Path("eval/datasets/research_use_cases.yaml")
    with open(out_path, "w", encoding="utf-8") as f:
        yaml.dump(all_cases, f, Dumper=IndentedDumper, sort_keys=False, width=1000)
    print(f"Successfully compiled all 30 cases into {out_path} ({out_path.stat().st_size} bytes)")
