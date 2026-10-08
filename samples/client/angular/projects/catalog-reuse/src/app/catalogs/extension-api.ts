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
import {ComponentApi, DynamicStringSchema, DynamicNumberSchema} from '@a2ui/web_core/v1_0';

/**
 * v1.0-Specific Component API.
 * Demonstrates component registered exclusively in the extension catalog
 * and resolved on a multi-catalog surface via `catalogId`.
 */
export const MetricGaugeApi = {
  name: 'MetricGauge',
  schema: z.object({
    label: DynamicStringSchema,
    score: DynamicNumberSchema,
    maxScore: DynamicNumberSchema.default(100),
    trend: z.enum(['up', 'down', 'stable']).default('stable'),
  }),
} satisfies ComponentApi;
