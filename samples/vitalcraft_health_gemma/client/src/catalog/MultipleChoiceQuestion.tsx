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

export const MultipleChoiceQuestionApi = {
  name: 'MultipleChoiceQuestion',
  schema: z.object({
    id: z.string().optional(),
    question: z.string().describe('The prompt question to ask the user'),
    options: z.array(z.string()).describe('Selectable choices'),
    selected: z
      .union([z.string(), z.array(z.string())])
      .optional()
      .describe('Selected choices'),
    multiSelect: z.boolean().optional().describe('Whether multiple choices are allowed'),
  }),
};

export const MultipleChoiceQuestion = createComponentImplementation(
  MultipleChoiceQuestionApi,
  ({props}) => {
    const initialSelected: string[] = Array.isArray(props.selected)
      ? props.selected
      : props.selected
        ? [props.selected]
        : [];

    const [selectedOptions, setSelectedOptions] = useState<string[]>(initialSelected);

    const handleSelect = (option: string) => {
      if (props.multiSelect) {
        setSelectedOptions(prev =>
          prev.includes(option) ? prev.filter(o => o !== option) : [...prev, option],
        );
      } else {
        setSelectedOptions([option]);
        // Dispatch custom choice event so the conversation seamlessly responds
        window.dispatchEvent(
          new CustomEvent('vitalcraft:choice-selected', {
            detail: {question: props.question, option},
          }),
        );
      }
    };

    return (
      <div className="mcq-card">
        <div className="mcq-question">❓ {props.question}</div>
        <div className="mcq-options">
          {props.options?.map((option: unknown, idx: number) => {
            const optStr = String(option);
            const isSelected = selectedOptions.includes(optStr);
            return (
              <button
                type="button"
                key={idx}
                className={`mcq-chip ${isSelected ? 'selected' : ''}`}
                onClick={() => handleSelect(optStr)}
              >
                {optStr}
              </button>
            );
          })}
        </div>
      </div>
    );
  },
);
