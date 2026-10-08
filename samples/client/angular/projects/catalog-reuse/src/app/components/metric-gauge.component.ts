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
import {MetricGaugeApi} from '../catalogs/extension-api';

@Component({
  selector: 'app-metric-gauge',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="gauge-container" [attr.data-testid]="'metric-gauge-' + componentId()">
      <div class="gauge-header">
        <span class="gauge-label">{{ label() }}</span>
        <div class="gauge-score-trend">
          <span class="gauge-score" data-testid="gauge-score">{{ score() }}</span>
          <span class="gauge-max">/ {{ maxScore() }}</span>
          <span class="trend-icon" [class]="trend()">
            @switch (trend()) {
              @case ('up') {
                ▲
              }
              @case ('down') {
                ▼
              }
              @default {
                ▶
              }
            }
          </span>
        </div>
      </div>
      <div class="gauge-bar-track">
        <div class="gauge-bar-fill" [style.width.%]="percentage()"></div>
      </div>
      <div class="gauge-footer">
        <span class="v1-badge">v1.0 Extension Catalog Component</span>
        <span class="percentage-label">{{ percentage() }}%</span>
      </div>
    </div>
  `,
  styles: [
    `
      .gauge-container {
        background: linear-gradient(135deg, #fdf4ff 0%, #fae8ff 100%);
        border: 2px solid #d946ef;
        border-radius: 10px;
        padding: 14px;
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin: 8px 0;
      }
      .gauge-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      .gauge-label {
        font-weight: 600;
        font-size: 0.95rem;
        color: #701a75;
      }
      .gauge-score-trend {
        display: flex;
        align-items: baseline;
        gap: 4px;
      }
      .gauge-score {
        font-size: 1.25rem;
        font-weight: 700;
        color: #a21caf;
      }
      .gauge-max {
        font-size: 0.85rem;
        color: #86198f;
      }
      .trend-icon {
        font-size: 0.85rem;
        margin-left: 4px;
      }
      .trend-icon.up {
        color: #16a34a;
      }
      .trend-icon.down {
        color: #dc2626;
      }
      .trend-icon.stable {
        color: #6b7280;
      }
      .gauge-bar-track {
        height: 10px;
        background-color: #f3e8ff;
        border-radius: 9999px;
        overflow: hidden;
      }
      .gauge-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #c026d3 0%, #ec4899 100%);
        transition: width 0.3s ease;
      }
      .gauge-footer {
        display: flex;
        justify-content: space-between;
        font-size: 0.75rem;
        color: #86198f;
      }
      .v1-badge {
        font-weight: 600;
        letter-spacing: 0.02em;
      }
      .percentage-label {
        font-weight: 600;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MetricGaugeComponent extends CatalogComponent<typeof MetricGaugeApi> {
  readonly label = computed(() => this.props()['label']?.value() || 'Metric');
  readonly score = computed(() => Number(this.props()['score']?.value() ?? 0));
  readonly maxScore = computed(() => Number(this.props()['maxScore']?.value() ?? 100));
  readonly trend = computed(() => this.props()['trend']?.value() || 'stable');
  readonly percentage = computed(() => {
    const max = this.maxScore() || 100;
    return Math.min(100, Math.max(0, Math.round((this.score() / max) * 100)));
  });
}
