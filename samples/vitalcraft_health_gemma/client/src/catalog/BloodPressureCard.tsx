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

export const BloodPressureCardApi = {
  name: 'BloodPressureCard',
  schema: z.object({
    id: z.string().optional(),
    systolic: z.number().describe('Systolic reading'),
    diastolic: z.number().describe('Diastolic reading'),
    pulse: z.number().optional().describe('Pulse bpm'),
    status: z.string().describe('Classification status'),
    trend: z.string().optional().describe('Trend text'),
    recordedAt: z.string().optional().describe('Recorded time'),
  }),
};

export const BloodPressureCard = createComponentImplementation(BloodPressureCardApi, ({props}) => {
  const isStage1 = props.status?.toLowerCase().includes('stage');
  const isElevated = props.status?.toLowerCase().includes('elevated');
  const badgeClass = isStage1 ? 'stage1' : isElevated ? 'elevated' : 'normal';

  return (
    <div className="bp-card">
      <div>
        <div className="bp-readings">
          <span className="bp-number">{props.systolic}</span>
          <span className="bp-unit">/ {props.diastolic} mmHg</span>
        </div>
        <div className="bp-meta">
          {props.recordedAt || 'Recent reading'} •{' '}
          {props.pulse ? `Pulse: ${props.pulse} bpm` : 'Resting'}
          {props.trend && <span> • {props.trend}</span>}
        </div>
      </div>
      <div className={`bp-status-badge ${badgeClass}`}>● {props.status}</div>
    </div>
  );
});
