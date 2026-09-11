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

import {useState} from 'react';
import {z} from 'zod';
import {createComponentImplementation} from '@a2ui/react/v0_9';

export const HealthPlanBuilderApi = {
  name: 'HealthPlanBuilder',
  schema: z.object({
    id: z.string().optional(),
    planTitle: z.string().describe('Name of the health plan'),
    targetMetric: z.string().describe('Target metric'),
    durationWeeks: z.number().optional().describe('Plan duration in weeks'),
    milestones: z.array(z.string()).describe('Milestones list'),
    status: z.string().optional().describe('Plan status'),
  }),
};

export const HealthPlanBuilder = createComponentImplementation(HealthPlanBuilderApi, ({props}) => {
  const [accepted, setAccepted] = useState(props.status === 'active');

  return (
    <div className="plan-card">
      <div className="plan-header">
        <div>
          <div className="plan-title">{props.planTitle}</div>
          <div className="plan-target">🎯 {props.targetMetric}</div>
        </div>
        {props.durationWeeks && (
          <span className="bp-meta" style={{fontWeight: 600}}>
            ⏱️ {props.durationWeeks} Weeks
          </span>
        )}
      </div>

      <div className="milestones-list">
        {props.milestones?.map((milestone: unknown, idx: number) => (
          <div key={idx} className="milestone-item">
            <span className="milestone-check">✓</span>
            <span>{String(milestone)}</span>
          </div>
        ))}
      </div>

      <button type="button" className="plan-action-btn" onClick={() => setAccepted(prev => !prev)}>
        {accepted ? '✓ Plan Active & Synced to Calendar' : 'Adopt Health Plan'}
      </button>
    </div>
  );
});
