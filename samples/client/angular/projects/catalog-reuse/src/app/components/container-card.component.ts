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
import {ContainerCardApi} from '../catalogs/common-api';

@Component({
  selector: 'app-container-card',
  standalone: true,
  imports: [CommonModule, ComponentHostComponent],
  template: `
    <div class="card-container" [attr.data-testid]="'container-card-' + componentId()">
      @if (title()) {
        <div class="card-header">
          <div class="header-titles">
            <h3 class="card-title">{{ title() }}</h3>
            @if (subtitle()) {
              <p class="card-subtitle">{{ subtitle() }}</p>
            }
          </div>
          @if (badge()) {
            <span class="card-badge">{{ badge() }}</span>
          }
        </div>
      }
      <div class="card-content">
        @if (child()) {
          <a2ui-v09-component-host
            [surfaceId]="surfaceId()"
            [componentKey]="child()!"
          ></a2ui-v09-component-host>
        }
        @if (children()) {
          @for (c of children(); track $index) {
            <a2ui-v09-component-host
              [surfaceId]="surfaceId()"
              [componentKey]="c"
            ></a2ui-v09-component-host>
          }
        }
      </div>
    </div>
  `,
  styles: [
    `
      .card-container {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
      }
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        border-bottom: 1px solid #f1f5f9;
        padding-bottom: 12px;
        margin-bottom: 14px;
      }
      .card-title {
        margin: 0;
        font-size: 1.15rem;
        font-weight: 600;
        color: #1e293b;
      }
      .card-subtitle {
        margin: 4px 0 0 0;
        font-size: 0.875rem;
        color: #64748b;
      }
      .card-badge {
        background-color: #e0e7ff;
        color: #4338ca;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 4px 8px;
        border-radius: 6px;
      }
      .card-content {
        display: flex;
        flex-direction: column;
        gap: 12px;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ContainerCardComponent extends CatalogComponent<typeof ContainerCardApi> {
  readonly title = computed(() => this.props()['title']?.value());
  readonly subtitle = computed(() => this.props()['subtitle']?.value());
  readonly badge = computed(() => this.props()['badge']?.value());
  readonly child = computed(() => this.props()['child']?.value());
  readonly children = computed(() => {
    const raw = this.props()['children']?.value();
    return Array.isArray(raw) ? raw : null;
  });
}
