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
import {CatalogComponent, ComponentHostComponent} from '@a2ui/angular/v0_9';
import {DynamicRepeaterApi} from '../catalogs/common-api';

@Component({
  selector: 'app-dynamic-repeater',
  standalone: true,
  imports: [CommonModule, ComponentHostComponent],
  template: `
    <div class="repeater-wrapper" [attr.data-testid]="'dynamic-repeater-' + componentId()">
      @if (title()) {
        <h4 class="repeater-title">{{ title() }}</h4>
      }
      <div class="items-grid">
        @for (item of items(); track $index) {
          <div class="repeater-cell" data-testid="repeater-item">
            <a2ui-v09-component-host
              [surfaceId]="surfaceId()"
              [componentKey]="item"
            ></a2ui-v09-component-host>
          </div>
        }
      </div>
    </div>
  `,
  styles: [
    `
      .repeater-wrapper {
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin: 8px 0;
      }
      .repeater-title {
        margin: 0;
        font-size: 0.95rem;
        font-weight: 600;
        color: #475569;
      }
      .items-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
      }
      .repeater-cell {
        display: inline-flex;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DynamicRepeaterComponent extends CatalogComponent<typeof DynamicRepeaterApi> {
  readonly title = computed(() => this.props()['title']?.value());
  readonly items = computed(() => {
    const raw = this.props()['children']?.value();
    return Array.isArray(raw) ? raw : [];
  });
}
