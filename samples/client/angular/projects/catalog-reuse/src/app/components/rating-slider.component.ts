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
import {RatingSliderApi} from '../catalogs/common-api';

@Component({
  selector: 'app-rating-slider',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="slider-wrapper" [attr.data-testid]="'rating-slider-' + componentId()">
      <div class="slider-header">
        <label class="slider-label" [for]="'slider-' + componentId()">
          {{ label() }}
        </label>
        <span class="value-badge" data-testid="slider-value-display">{{ value() }}</span>
      </div>
      <input
        [id]="'slider-' + componentId()"
        type="range"
        class="range-input"
        [min]="min()"
        [max]="max()"
        [value]="value()"
        (input)="handleInput($event)"
      />
      <div class="range-limits">
        <span>{{ min() }}</span>
        <span>{{ max() }}</span>
      </div>
    </div>
  `,
  styles: [
    `
      .slider-wrapper {
        display: flex;
        flex-direction: column;
        gap: 6px;
        padding: 8px 0;
      }
      .slider-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      .slider-label {
        font-size: 0.875rem;
        font-weight: 500;
        color: #334155;
      }
      .value-badge {
        background-color: #f1f5f9;
        border: 1px solid #cbd5e1;
        padding: 2px 8px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.85rem;
        color: #1e293b;
      }
      .range-input {
        width: 100%;
        accent-color: #2563eb;
        cursor: pointer;
      }
      .range-limits {
        display: flex;
        justify-content: space-between;
        font-size: 0.75rem;
        color: #94a3b8;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RatingSliderComponent extends CatalogComponent<typeof RatingSliderApi> {
  readonly label = computed(() => this.props()['label']?.value() || 'Rating');
  readonly min = computed(() => this.props()['min']?.value() ?? 0);
  readonly max = computed(() => this.props()['max']?.value() ?? 10);
  readonly value = computed(() => Number(this.props()['value']?.value() ?? 0));

  handleInput(event: Event) {
    const val = Number((event.target as HTMLInputElement).value);
    this.props()['value']?.onUpdate(val);
  }
}
