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
import {
  ComponentApi,
  DynamicStringSchema,
  DynamicNumberSchema,
  DynamicBooleanSchema,
  ComponentIdSchema,
  ChildListSchema,
  ActionSchema,
} from '@a2ui/web_core/v1_0';

/**
 * Permissive CheckRule schema supporting both v0.9 (condition: boolean, message: string required)
 * and v1.0 (condition: object returning CheckResult, message: string optional).
 */
export const DualProtocolCheckRuleSchema = z.object({
  condition: z.any(),
  message: z.string().optional(),
});

export const ContainerCardApi = {
  name: 'ContainerCard',
  schema: z.object({
    title: DynamicStringSchema.optional(),
    subtitle: DynamicStringSchema.optional(),
    badge: DynamicStringSchema.optional(),
    child: ComponentIdSchema.optional(),
    children: ChildListSchema.optional(),
  }),
} satisfies ComponentApi;

export const SmartInputApi = {
  name: 'SmartInput',
  schema: z.object({
    label: DynamicStringSchema,
    placeholder: DynamicStringSchema.optional(),
    value: DynamicStringSchema.optional(),
    checks: z.array(DualProtocolCheckRuleSchema).optional(),
  }),
} satisfies ComponentApi;

export const RatingSliderApi = {
  name: 'RatingSlider',
  schema: z.object({
    label: DynamicStringSchema,
    min: z.number().default(0),
    max: z.number().default(10),
    value: DynamicNumberSchema.optional(),
  }),
} satisfies ComponentApi;

export const DynamicRepeaterApi = {
  name: 'DynamicRepeater',
  schema: z.object({
    title: DynamicStringSchema.optional(),
    children: ChildListSchema,
  }),
} satisfies ComponentApi;

export const ActionTriggerApi = {
  name: 'ActionTrigger',
  schema: z.object({
    label: DynamicStringSchema,
    variant: z.enum(['primary', 'secondary', 'danger']).default('primary'),
    disabled: DynamicBooleanSchema.optional(),
    action: ActionSchema.optional(),
  }),
} satisfies ComponentApi;

export const ComputedSummaryApi = {
  name: 'ComputedSummary',
  schema: z.object({
    title: DynamicStringSchema,
    greeting: DynamicStringSchema.optional(),
    total: DynamicNumberSchema.optional(),
  }),
} satisfies ComponentApi;

export const StatusBadgeApi = {
  name: 'StatusBadge',
  schema: z.object({
    text: DynamicStringSchema,
    variant: z.enum(['success', 'warning', 'info']).default('info'),
  }),
} satisfies ComponentApi;
