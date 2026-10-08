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

import {ChangeDetectionStrategy, Component, computed} from '@angular/core';
import {CommonModule} from '@angular/common';
import {CatalogComponent} from '@a2ui/angular/v0_9';
import {ComputedSummaryApi} from '../catalogs/common-api';

@Component({
  selector: 'app-computed-summary',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="summary-box" [attr.data-testid]="'computed-summary-' + componentId()">
      <h4 class="summary-title">{{ title() }}</h4>
      <div class="summary-row">
        <span class="summary-label">Greeting:</span>
        <span class="summary-value" data-testid="summary-greeting">{{ greeting() }}</span>
      </div>
      <div class="summary-row">
        <span class="summary-label">Calculated Subtotal:</span>
        <span class="summary-value" data-testid="summary-total">\${{ total() }}</span>
      </div>
    </div>
  `,
  styles: [
    `
      .summary-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 14px;
        display: flex;
        flex-direction: column;
        gap: 8px;
      }
      .summary-title {
        margin: 0 0 4px 0;
        font-size: 1rem;
        font-weight: 600;
        color: #1e293b;
      }
      .summary-row {
        display: flex;
        justify-content: space-between;
        font-size: 0.9rem;
      }
      .summary-label {
        color: #64748b;
      }
      .summary-value {
        font-weight: 600;
        color: #0f172a;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ComputedSummaryComponent extends CatalogComponent<typeof ComputedSummaryApi> {
  readonly title = computed(() => this.props()['title']?.value() || 'Summary');
  readonly greeting = computed(() => this.props()['greeting']?.value() || 'Hello!');
  readonly total = computed(() => Number(this.props()['total']?.value() ?? 0));
}
