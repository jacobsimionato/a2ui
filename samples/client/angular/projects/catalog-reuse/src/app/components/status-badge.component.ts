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
import {StatusBadgeApi} from '../catalogs/common-api';

@Component({
  selector: 'app-status-badge',
  standalone: true,
  imports: [CommonModule],
  template: `
    <span
      class="badge-pill"
      [class]="'badge-pill ' + variant()"
      [attr.data-testid]="'status-badge-' + componentId()"
    >
      {{ text() }}
    </span>
  `,
  styles: [
    `
      .badge-pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 500;
      }
      .badge-pill.info {
        background-color: #e0f2fe;
        color: #0369a1;
      }
      .badge-pill.success {
        background-color: #dcfce7;
        color: #15803d;
      }
      .badge-pill.warning {
        background-color: #fef9c3;
        color: #a16207;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class StatusBadgeComponent extends CatalogComponent<typeof StatusBadgeApi> {
  readonly text = computed(() => this.props()['text']?.value() || '');
  readonly variant = computed(() => this.props()['variant']?.value() || 'info');
}
