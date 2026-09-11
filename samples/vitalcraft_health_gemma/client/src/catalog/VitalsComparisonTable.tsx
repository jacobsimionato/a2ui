/*
 * Copyright 2024 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import {z} from 'zod';
import {createComponentImplementation} from '@a2ui/react/v0_9';

export const VitalsComparisonTableApi = {
  name: 'VitalsComparisonTable',
  schema: z.object({
    id: z.string().optional(),
    headers: z.array(z.string()).describe('Table headers'),
    rows: z.array(z.array(z.string())).describe('Table rows'),
    highlightMetric: z.string().optional().describe('Metric to highlight'),
  }),
};

export const VitalsComparisonTable = createComponentImplementation(
  VitalsComparisonTableApi,
  ({props}) => {
    return (
      <div className="vitals-table-card">
        <table className="vitals-table">
          <thead>
            <tr>
              {props.headers?.map((header: unknown, idx: number) => (
                <th key={idx}>{String(header)}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {props.rows?.map((row: unknown, rowIdx: number) => {
              const rowArr = Array.isArray(row) ? row : [];
              const isHighlighted =
                props.highlightMetric &&
                rowArr.some((cell: unknown) =>
                  String(cell).toLowerCase().includes(props.highlightMetric!.toLowerCase()),
                );
              return (
                <tr key={rowIdx} className={isHighlighted ? 'highlighted' : ''}>
                  {rowArr.map((cell: unknown, cellIdx: number) => (
                    <td key={cellIdx}>{String(cell)}</td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    );
  },
);
