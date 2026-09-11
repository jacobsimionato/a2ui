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

const HabitItemSchema = z.object({
  id: z.string(),
  name: z.string(),
  streakDays: z.number().optional(),
  completedToday: z.boolean(),
  category: z.string().optional(),
});

type HabitItem = z.infer<typeof HabitItemSchema>;

export const HabitTrackerApi = {
  name: 'HabitTracker',
  schema: z.object({
    id: z.string().optional(),
    title: z.string().describe('Habit group title'),
    habits: z.array(HabitItemSchema).describe('Habits list'),
  }),
};

export const HabitTracker = createComponentImplementation(HabitTrackerApi, ({props}) => {
  const [habitsState, setHabitsState] = useState<HabitItem[]>(
    props.habits?.map((h: HabitItem) => ({...h})) || [],
  );

  const toggleHabit = (id: string) => {
    setHabitsState((prev: HabitItem[]) =>
      prev.map((h: HabitItem) => {
        if (h.id === id) {
          const nextCompleted = !h.completedToday;
          const streakAdjustment = nextCompleted ? 1 : -1;
          return {
            ...h,
            completedToday: nextCompleted,
            streakDays: Math.max(0, (h.streakDays || 0) + streakAdjustment),
          };
        }
        return h;
      }),
    );
  };

  return (
    <div className="habit-card">
      <div className="habit-title">🔥 {props.title}</div>
      <div className="habits-grid">
        {habitsState.map((habit: HabitItem) => (
          <div
            key={habit.id}
            className={`habit-tile ${habit.completedToday ? 'completed' : ''}`}
            onClick={() => toggleHabit(habit.id)}
          >
            <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
              <span
                style={{
                  color: habit.completedToday ? 'var(--accent-emerald)' : 'var(--text-muted)',
                  fontSize: '15px',
                }}
              >
                {habit.completedToday ? '☑' : '☐'}
              </span>
              <span style={{fontSize: '13px', fontWeight: 500}}>{habit.name}</span>
            </div>
            {habit.streakDays !== undefined && habit.streakDays > 0 && (
              <span className="streak-badge">⚡ {habit.streakDays}d</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
});
