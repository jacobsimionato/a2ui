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

import {Injectable} from '@angular/core';
import {z} from 'zod';
import {
  AngularCatalog,
  AngularComponentImplementation,
  createComponentImplementation,
} from '@a2ui/angular/v0_9';
import {
  createFunctionImplementation,
  DynamicStringSchema,
  DynamicNumberSchema,
  FunctionImplementation,
} from '@a2ui/web_core/v1_0';

// Component APIs
import {
  ContainerCardApi,
  SmartInputApi,
  RatingSliderApi,
  DynamicRepeaterApi,
  ActionTriggerApi,
  ComputedSummaryApi,
  StatusBadgeApi,
} from './common-api';
import {MetricGaugeApi} from './extension-api';

// Angular Component Implementations
import {ContainerCardComponent} from '../components/container-card.component';
import {SmartInputComponent} from '../components/smart-input.component';
import {RatingSliderComponent} from '../components/rating-slider.component';
import {DynamicRepeaterComponent} from '../components/dynamic-repeater.component';
import {ActionTriggerComponent} from '../components/action-trigger.component';
import {ComputedSummaryComponent} from '../components/computed-summary.component';
import {StatusBadgeComponent} from '../components/status-badge.component';
import {MetricGaugeComponent} from '../components/metric-gauge.component';

/**
 * 100% Shared Component Implementations across v0.9 and v1.0.
 * The exact same Angular `@Component` classes and `ComponentApi` descriptors are reused.
 */
export const SHARED_COMPONENT_IMPLEMENTATIONS: AngularComponentImplementation[] = [
  createComponentImplementation(ContainerCardApi, ContainerCardComponent),
  createComponentImplementation(SmartInputApi, SmartInputComponent),
  createComponentImplementation(RatingSliderApi, RatingSliderComponent),
  createComponentImplementation(DynamicRepeaterApi, DynamicRepeaterComponent),
  createComponentImplementation(ActionTriggerApi, ActionTriggerComponent),
  createComponentImplementation(ComputedSummaryApi, ComputedSummaryComponent),
  createComponentImplementation(StatusBadgeApi, StatusBadgeComponent),
];

/**
 * Shared Functions: string formatting and calculation logic.
 * Note: Arguments use DynamicStringSchema/DynamicNumberSchema to allow wire-level data bindings and expressions.
 */
export const formatGreetingFunction = createFunctionImplementation(
  {
    name: 'formatGreeting',
    returnType: 'string',
    schema: z.object({
      name: DynamicStringSchema.optional(),
    }),
  },
  args => {
    const name = args.name ? String(args.name).trim() : 'Guest';
    return `Welcome back, ${name}!`;
  },
);

export const calculateTotalFunction = createFunctionImplementation(
  {
    name: 'calculateTotal',
    returnType: 'number',
    schema: z.object({
      quantity: DynamicNumberSchema.optional(),
      unitPrice: DynamicNumberSchema.optional(),
    }),
  },
  args => {
    const qty = Number(args.quantity ?? 1);
    const price = Number(args.unitPrice ?? 10);
    return qty * price;
  },
);

/**
 * v0.9 Validation Function (returns primitive boolean).
 */
export const checkRequiredV09Function = createFunctionImplementation(
  {
    name: 'checkRequired',
    returnType: 'boolean',
    schema: z.object({
      value: DynamicStringSchema.optional(),
    }),
  },
  args => {
    const val = args.value;
    return val !== undefined && val !== null && String(val).trim().length > 0;
  },
);

/**
 * v1.0 Validation Function (returns structured CheckResult object).
 */
export const checkRequiredV10Function = createFunctionImplementation(
  {
    name: 'checkRequiredV1',
    returnType: 'object',
    schema: z.object({
      value: DynamicStringSchema.optional(),
    }),
  },
  args => {
    const val = args.value;
    const isValid = val !== undefined && val !== null && String(val).trim().length > 0;
    return {
      valid: isValid,
      severity: 'error',
      message: isValid ? '' : 'Customer name is required by v1.0 CheckResult',
      code: 'REQUIRED',
    };
  },
);

export const SHARED_FUNCTIONS: FunctionImplementation[] = [
  formatGreetingFunction,
  calculateTotalFunction,
  checkRequiredV09Function,
  checkRequiredV10Function,
];

export const V09_CATALOG_ID = 'https://example.com/catalogs/common/v0_9/catalog.json';
export const V10_CATALOG_ID = 'https://example.com/catalogs/common/v1_0/catalog.json';
export const V10_EXTENSION_CATALOG_ID = 'https://example.com/catalogs/v1_extension/catalog.json';

/**
 * v0.9 Common Catalog instance:
 * Declares protocolVersion '0.9', references shared components and functions.
 */
@Injectable({providedIn: 'root'})
export class CommonCatalogV09 extends AngularCatalog {
  constructor() {
    super(V09_CATALOG_ID, '0.9', SHARED_COMPONENT_IMPLEMENTATIONS, SHARED_FUNCTIONS);
  }
}

/**
 * v1.0 Common Catalog instance:
 * Declares protocolVersion '1.0', REUSING the exact same shared components and functions!
 */
@Injectable({providedIn: 'root'})
export class CommonCatalogV10 extends AngularCatalog {
  constructor() {
    super(V10_CATALOG_ID, '1.0', SHARED_COMPONENT_IMPLEMENTATIONS, SHARED_FUNCTIONS);
  }
}

/**
 * v1.0 Extension Catalog instance:
 * Declares protocolVersion '1.0', provides v1.0-only MetricGauge component.
 */
@Injectable({providedIn: 'root'})
export class ExtensionCatalogV10 extends AngularCatalog {
  constructor() {
    super(V10_EXTENSION_CATALOG_ID, '1.0', [
      createComponentImplementation(MetricGaugeApi, MetricGaugeComponent),
    ]);
  }
}
