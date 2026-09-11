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

export const ExerciseLogCardApi = {
  name: 'ExerciseLogCard',
  schema: z.object({
    id: z.string().optional(),
    activity: z.string().describe('Activity name'),
    durationMinutes: z.number().describe('Duration in minutes'),
    avgHeartRate: z.number().optional().describe('Heart rate bpm'),
    calories: z.number().optional().describe('Calories burned'),
    intensity: z.string().optional().describe('Workout intensity'),
    date: z.string().optional().describe('Workout date'),
    notes: z.string().optional().describe('Workout notes'),
  }),
};

export const ExerciseLogCard = createComponentImplementation(ExerciseLogCardApi, ({props}) => {
  return (
    <div className="exercise-card">
      <div className="exercise-title-group">
        <div className="exercise-icon-box">🏃</div>
        <div>
          <div style={{fontWeight: 700, fontSize: '15px'}}>{props.activity}</div>
          <div className="bp-meta">
            {props.date || 'Recent workout'}
            {props.intensity && <span> • {props.intensity} Intensity</span>}
            {props.notes && <span> • {props.notes}</span>}
          </div>
        </div>
      </div>
      <div className="exercise-stats">
        <div>
          <span className="stat-pill">{props.durationMinutes}</span> min
        </div>
        {props.calories && (
          <div>
            <span className="stat-pill">{props.calories}</span> kcal
          </div>
        )}
        {props.avgHeartRate && (
          <div>
            <span className="stat-pill">{props.avgHeartRate}</span> bpm
          </div>
        )}
      </div>
    </div>
  );
});
