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

import {Catalog} from '@a2ui/web_core/v0_9';
import type {ReactComponentImplementation} from '@a2ui/react/v0_9';

import {BloodPressureCard} from './BloodPressureCard';
import {ExerciseLogCard} from './ExerciseLogCard';
import {HealthPlanBuilder} from './HealthPlanBuilder';
import {VitalsComparisonTable} from './VitalsComparisonTable';
import {VitalsTrendChart} from './VitalsTrendChart';
import {HabitTracker} from './HabitTracker';
import {MultipleChoiceQuestion} from './MultipleChoiceQuestion';
import {IntensityPicker} from './IntensityPicker';

export const vitalcraftComponents: ReactComponentImplementation[] = [
  BloodPressureCard,
  ExerciseLogCard,
  HealthPlanBuilder,
  VitalsComparisonTable,
  VitalsTrendChart,
  HabitTracker,
  MultipleChoiceQuestion,
  IntensityPicker,
];

export const VITALCRAFT_CATALOG_ID = 'https://a2ui.org/catalogs/vitalcraft_health.json';

export const vitalcraftCatalog = new Catalog<ReactComponentImplementation>(
  VITALCRAFT_CATALOG_ID,
  vitalcraftComponents,
);

export {
  BloodPressureCard,
  ExerciseLogCard,
  HealthPlanBuilder,
  VitalsComparisonTable,
  VitalsTrendChart,
  HabitTracker,
  MultipleChoiceQuestion,
  IntensityPicker,
};
