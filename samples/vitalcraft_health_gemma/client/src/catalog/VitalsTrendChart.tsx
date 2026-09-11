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

export const VitalsTrendChartApi = {
  name: 'VitalsTrendChart',
  schema: z.object({
    id: z.string().optional(),
    title: z.string().describe('Chart title'),
    metric: z.string().describe('Metric type'),
    labels: z.array(z.string()).describe('X-axis labels'),
    systolicValues: z.array(z.number()).optional(),
    diastolicValues: z.array(z.number()).optional(),
    exerciseMinutes: z.array(z.number()).optional(),
    targetThreshold: z.number().optional(),
  }),
};

export const VitalsTrendChart = createComponentImplementation(VitalsTrendChartApi, ({props}) => {
  const isBp = props.metric === 'blood_pressure';
  const width = 480;
  const height = 150;
  const padding = 28;

  const labels = props.labels || ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const n = labels.length;

  const getY = (val: number, minVal: number, maxVal: number) => {
    const clamped = Math.max(minVal, Math.min(maxVal, val));
    const normalized = (clamped - minVal) / (maxVal - minVal);
    return height - padding - normalized * (height - 2 * padding);
  };

  const getX = (idx: number) => {
    return padding + (idx / Math.max(1, n - 1)) * (width - 2 * padding);
  };

  let systolicPath = '';
  let diastolicPath = '';
  let exerciseBars: {x: number; y: number; h: number; val: number}[] = [];

  if (isBp && props.systolicValues && props.diastolicValues) {
    const minVal = 70;
    const maxVal = 150;
    systolicPath = props.systolicValues
      .map((v: number, i: number) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(v, minVal, maxVal)}`)
      .join(' ');
    diastolicPath = props.diastolicValues
      .map((v: number, i: number) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(v, minVal, maxVal)}`)
      .join(' ');
  } else if (props.exerciseMinutes) {
    const maxVal = 60;
    exerciseBars = props.exerciseMinutes.map((v: number, i: number) => {
      const x = getX(i) - 12;
      const y = getY(v, 0, maxVal);
      const h = height - padding - y;
      return {x, y, h: Math.max(2, h), val: v};
    });
  }

  return (
    <div className="trend-chart-card">
      <div className="chart-header">
        <div className="chart-title">{props.title}</div>
        <div className="chart-legend">
          {isBp ? (
            <>
              <div className="legend-item">
                <span className="legend-color" style={{background: '#f43f5e'}} />
                <span>Systolic</span>
              </div>
              <div className="legend-item">
                <span className="legend-color" style={{background: '#38bdf8'}} />
                <span>Diastolic</span>
              </div>
              <div className="legend-item">
                <span className="legend-color" style={{background: '#10b981'}} />
                <span>Target (&lt;120)</span>
              </div>
            </>
          ) : (
            <div className="legend-item">
              <span className="legend-color" style={{background: '#10b981'}} />
              <span>Minutes</span>
            </div>
          )}
        </div>
      </div>

      <svg viewBox={`0 0 ${width} ${height}`} style={{width: '100%', height: 'auto'}}>
        {/* Target guideline threshold */}
        {props.targetThreshold && isBp && (
          <line
            x1={padding}
            y1={getY(props.targetThreshold, 70, 150)}
            x2={width - padding}
            y2={getY(props.targetThreshold, 70, 150)}
            stroke="#10b981"
            strokeDasharray="4 4"
            strokeWidth="1.5"
            opacity="0.6"
          />
        )}

        {/* Lines / Bars */}
        {isBp ? (
          <>
            <path d={systolicPath} fill="none" stroke="#f43f5e" strokeWidth="2.5" />
            <path d={diastolicPath} fill="none" stroke="#38bdf8" strokeWidth="2.5" />
            {props.systolicValues?.map((v: number, i: number) => (
              <circle key={`sys-${i}`} cx={getX(i)} cy={getY(v, 70, 150)} r="3.5" fill="#f43f5e" />
            ))}
            {props.diastolicValues?.map((v: number, i: number) => (
              <circle key={`dia-${i}`} cx={getX(i)} cy={getY(v, 70, 150)} r="3.5" fill="#38bdf8" />
            ))}
          </>
        ) : (
          exerciseBars.map((b, i: number) => (
            <rect
              key={`bar-${i}`}
              x={b.x}
              y={b.y}
              width="24"
              height={b.h}
              rx="4"
              fill="#10b981"
              opacity="0.85"
            />
          ))
        )}

        {/* X axis labels */}
        {labels.map((l: unknown, i: number) => (
          <text
            key={`lbl-${i}`}
            x={getX(i)}
            y={height - 8}
            textAnchor="middle"
            fill="#94a3b8"
            fontSize="10.5"
            fontWeight="500"
          >
            {String(l)}
          </text>
        ))}
      </svg>
    </div>
  );
});
