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

import {test, expect} from '@playwright/test';

test.describe('A2UI Dual-Protocol (v0.9 & v1.0) Catalog Reuse', () => {
  test('Backend serves valid v0.9 and v1.0 catalog schemas', async ({request}) => {
    // 1. v0.9 Catalog JSON
    const v09Res = await request.get('/catalogs/common/v0_9/catalog.json');
    expect(v09Res.status()).toBe(200);
    const v09Json = await v09Res.json();
    expect(v09Json.catalogId).toBe('https://example.com/catalogs/common/v0_9/catalog.json');
    expect(v09Json.components.ContainerCard).toBeDefined();
    expect(v09Json.components.SmartInput).toBeDefined();
    expect(v09Json.functions.checkRequired.returnType).toBe('boolean');

    // 2. v1.0 Catalog JSON
    const v10Res = await request.get('/catalogs/common/v1_0/catalog.json');
    expect(v10Res.status()).toBe(200);
    const v10Json = await v10Res.json();
    expect(v10Json.catalogId).toBe('https://example.com/catalogs/common/v1_0/catalog.json');
    expect(v10Json.protocolVersion).toBe('1.0');
    expect(v10Json.components.ContainerCard).toBeDefined();
    expect(v10Json.components.SmartInput).toBeDefined();
    expect(v10Json.functions.checkRequiredV1.returnType).toBe('object');

    // 3. v1.0 Extension Catalog JSON
    const extRes = await request.get('/catalogs/v1_extension/catalog.json');
    expect(extRes.status()).toBe(200);
    const extJson = await extRes.json();
    expect(extJson.catalogId).toBe('https://example.com/catalogs/v1_extension/catalog.json');
    expect(extJson.protocolVersion).toBe('1.0');
    expect(extJson.components.MetricGauge).toBeDefined();
  });

  test('Renders both v0.9 and v1.0 surfaces side-by-side with shared components', async ({
    page,
  }) => {
    await page.goto('/');

    // Verify both columns exist
    const v09Col = page.locator('[data-testid="v09-column"]');
    const v10Col = page.locator('[data-testid="v10-column"]');
    await expect(v09Col).toBeVisible();
    await expect(v10Col).toBeVisible();

    // -------------------------------------------------------------
    // Verify v0.9 Surface Renderings
    // -------------------------------------------------------------
    await expect(v09Col.locator('text=Order Review (v0.9 Protocol)')).toBeVisible();
    await expect(v09Col.locator('text=v0.9 Active')).toBeVisible();

    // SmartInput initial state
    const v09Input = v09Col.locator('input[type="text"]');
    await expect(v09Input).toHaveValue('Jane Doe');

    // RatingSlider initial state
    await expect(v09Col.locator('[data-testid="slider-value-display"]')).toHaveText('4');

    // ComputedSummary (Function execution: formatGreeting + calculateTotal)
    await expect(v09Col.locator('[data-testid="summary-greeting"]')).toHaveText(
      'Welcome back, Jane Doe!',
    );
    await expect(v09Col.locator('[data-testid="summary-total"]')).toHaveText('$100');

    // DynamicRepeater (Child templates)
    const v09Items = v09Col.locator('[data-testid="repeater-item"]');
    await expect(v09Items).toHaveCount(3);
    await expect(v09Items.nth(0)).toHaveText('Premium Cloud Widget');
    await expect(v09Items.nth(1)).toHaveText('Universal Power Adapter');
    await expect(v09Items.nth(2)).toHaveText('High-Speed USB-C Cable');

    // ActionTrigger
    await expect(v09Col.locator('[data-testid="action-trigger-submitBtn"]')).toHaveText(
      'Submit Order (v0.9)',
    );

    // -------------------------------------------------------------
    // Verify v1.0 Surface Renderings (Shared Components + Extension)
    // -------------------------------------------------------------
    await expect(v10Col.locator('text=Order Review (v1.0 Protocol)')).toBeVisible();
    await expect(v10Col.locator('text=v1.0 Active')).toBeVisible();

    // SmartInput initial state
    const v10Input = v10Col.locator('input[type="text"]');
    await expect(v10Input).toHaveValue('John Smith');

    // RatingSlider initial state
    await expect(v10Col.locator('[data-testid="slider-value-display"]')).toHaveText('6');

    // MetricGauge (from the v1.0 Extension Catalog!)
    const gauge = v10Col.locator('[data-testid="metric-gauge-gaugeCard"]');
    await expect(gauge).toBeVisible();
    await expect(gauge.locator('text=Customer SLA Satisfaction Index')).toBeVisible();
    await expect(gauge.locator('[data-testid="gauge-score"]')).toHaveText('85');
    await expect(gauge.locator('text=/ 100')).toBeVisible();
    await expect(gauge.locator('text=85%')).toBeVisible();

    // ComputedSummary
    await expect(v10Col.locator('[data-testid="summary-greeting"]')).toHaveText(
      'Welcome back, John Smith!',
    );
    await expect(v10Col.locator('[data-testid="summary-total"]')).toHaveText('$150');

    // DynamicRepeater
    const v10Items = v10Col.locator('[data-testid="repeater-item"]');
    await expect(v10Items).toHaveCount(2);
    await expect(v10Items.nth(0)).toHaveText('Enterprise AI Cluster');
    await expect(v10Items.nth(1)).toHaveText('Dedicated Fiber Interconnect');

    // ActionTrigger
    await expect(v10Col.locator('[data-testid="action-trigger-submitBtn"]')).toHaveText(
      'Submit Order (v1.0)',
    );
  });

  test('Two-way data binding and function re-evaluation in v0.9 and v1.0', async ({page}) => {
    await page.goto('/');

    const v09Col = page.locator('[data-testid="v09-column"]');
    const v10Col = page.locator('[data-testid="v10-column"]');

    // 1. Test v0.9 two-way typing & reactive function calculation
    const v09Input = v09Col.locator('input[type="text"]');
    await v09Input.fill('Alice Walker');
    await expect(v09Col.locator('[data-testid="summary-greeting"]')).toHaveText(
      'Welcome back, Alice Walker!',
    );

    // 2. Test v0.9 slider update
    const v09Slider = v09Col.locator('input[type="range"]');
    await v09Slider.fill('8');
    await expect(v09Col.locator('[data-testid="slider-value-display"]')).toHaveText('8');
    await expect(v09Col.locator('[data-testid="summary-total"]')).toHaveText('$200');

    // 3. Test v1.0 two-way typing & reactive function calculation
    const v10Input = v10Col.locator('input[type="text"]');
    await v10Input.fill('Robert Green');
    await expect(v10Col.locator('[data-testid="summary-greeting"]')).toHaveText(
      'Welcome back, Robert Green!',
    );

    // 4. Test v1.0 slider update
    const v10Slider = v10Col.locator('input[type="range"]');
    await v10Slider.fill('10');
    await expect(v10Col.locator('[data-testid="slider-value-display"]')).toHaveText('10');
    await expect(v10Col.locator('[data-testid="summary-total"]')).toHaveText('$250');
  });

  test('Validation checks semantics: v0.9 boolean error vs v1.0 CheckResult error', async ({
    page,
  }) => {
    await page.goto('/');

    const v09Col = page.locator('[data-testid="v09-column"]');
    const v10Col = page.locator('[data-testid="v10-column"]');

    // 1. Clear v0.9 input to trigger v0.9 CheckRule
    const v09Input = v09Col.locator('input[type="text"]');
    await v09Input.fill('');
    await expect(v09Col.locator('[data-testid="validation-errors"]')).toBeVisible();
    await expect(v09Col.locator('[data-testid="validation-errors"]')).toHaveText(
      'Customer name is required',
    );

    // 2. Clear v1.0 input to trigger v1.0 CheckRule with CheckResult
    const v10Input = v10Col.locator('input[type="text"]');
    await v10Input.fill('');
    await expect(v10Col.locator('[data-testid="validation-errors"]')).toBeVisible();
    await expect(v10Col.locator('[data-testid="validation-errors"]')).toHaveText(
      'Customer name is required by v1.0 CheckResult',
    );
  });

  test('User interaction triggers actions dispatched to renderer listener', async ({page}) => {
    await page.goto('/');

    const v09Btn = page.locator(
      '[data-testid="v09-column"] [data-testid="action-trigger-submitBtn"]',
    );
    await v09Btn.click();

    const actionLog = page.locator('[data-testid="action-log"]');
    await expect(actionLog).toContainText('submitOrder');
    await expect(actionLog).toContainText('Jane Doe');

    const v10Btn = page.locator(
      '[data-testid="v10-column"] [data-testid="action-trigger-submitBtn"]',
    );
    await v10Btn.click();

    await expect(actionLog).toContainText('John Smith');
  });

  test('Tab switcher switches views smoothly', async ({page}) => {
    await page.goto('/');

    // Switch to v0.9 only
    await page.click('[data-testid="tab-v09"]');
    await expect(page.locator('[data-testid="v09-column"]')).toBeVisible();
    await expect(page.locator('[data-testid="v10-column"]')).not.toBeVisible();

    // Switch to v1.0 only
    await page.click('[data-testid="tab-v10"]');
    await expect(page.locator('[data-testid="v10-column"]')).toBeVisible();
    await expect(page.locator('[data-testid="v09-column"]')).not.toBeVisible();

    // Switch back to All
    await page.click('[data-testid="tab-all"]');
    await expect(page.locator('[data-testid="v09-column"]')).toBeVisible();
    await expect(page.locator('[data-testid="v10-column"]')).toBeVisible();
  });
});
