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

export const IntensityPickerApi = {
  name: 'IntensityPicker',
  schema: z.object({
    id: z.string().optional(),
    label: z.string().describe('Label for intensity picker'),
    selected: z.number().describe('Selected level'),
    min: z.number().optional().default(1),
    max: z.number().optional().default(10),
  }),
};

export const IntensityPicker = createComponentImplementation(IntensityPickerApi, ({props}) => {
  const minVal = props.min ?? 1;
  const maxVal = props.max ?? 10;
  const [currentVal, setCurrentVal] = useState(props.selected || minVal);

  const steps = [];
  for (let i = minVal; i <= maxVal; i++) {
    steps.push(i);
  }

  return (
    <div className="intensity-card">
      <div className="intensity-label">
        {props.label}: <span style={{color: 'var(--accent-cyan)'}}>Level {currentVal}</span>
      </div>
      <div className="intensity-stepper">
        {steps.map(step => (
          <button
            type="button"
            key={step}
            className={`intensity-step ${currentVal === step ? 'active' : ''}`}
            onClick={() => setCurrentVal(step)}
          >
            {step}
          </button>
        ))}
      </div>
    </div>
  );
});
