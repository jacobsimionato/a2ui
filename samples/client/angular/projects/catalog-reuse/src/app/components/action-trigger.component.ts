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

import {ChangeDetectionStrategy, Component, computed, inject} from '@angular/core';
import {CommonModule} from '@angular/common';
import {CatalogComponent, A2uiRendererService} from '@a2ui/angular/v0_9';
import {ActionTriggerApi} from '../catalogs/common-api';

@Component({
  selector: 'app-action-trigger',
  standalone: true,
  imports: [CommonModule],
  template: `
    <button
      type="button"
      class="action-btn"
      [class]="'action-btn ' + variant()"
      [disabled]="disabled()"
      [attr.data-testid]="'action-trigger-' + componentId()"
      (click)="handleClick()"
    >
      {{ label() }}
    </button>
  `,
  styles: [
    `
      .action-btn {
        padding: 10px 18px;
        border-radius: 6px;
        font-size: 0.95rem;
        font-weight: 600;
        cursor: pointer;
        border: none;
        transition: all 0.15s ease;
      }
      .action-btn.primary {
        background-color: #2563eb;
        color: #ffffff;
      }
      .action-btn.primary:hover:not(:disabled) {
        background-color: #1d4ed8;
      }
      .action-btn.secondary {
        background-color: #e2e8f0;
        color: #1e293b;
      }
      .action-btn.danger {
        background-color: #dc2626;
        color: #ffffff;
      }
      .action-btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        background-color: #cbd5e1;
        color: #64748b;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ActionTriggerComponent extends CatalogComponent<typeof ActionTriggerApi> {
  private rendererService = inject(A2uiRendererService);

  readonly label = computed(() => this.props()['label']?.value() || 'Action');
  readonly variant = computed(() => this.props()['variant']?.value() || 'primary');
  readonly disabled = computed(() => Boolean(this.props()['disabled']?.value()));

  handleClick() {
    const action = this.props()['action']?.value() as any;
    const surface = this.rendererService.surfaceGroup?.getSurface(this.surfaceId());
    if (surface && action) {
      void surface.dispatchAction(action, this.componentId());
    }
  }
}
