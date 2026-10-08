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
import {SmartInputApi} from '../catalogs/common-api';

@Component({
  selector: 'app-smart-input',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="input-group" [attr.data-testid]="'smart-input-' + componentId()">
      <label class="input-label" [for]="'input-' + componentId()">
        {{ label() }}
      </label>
      <input
        [id]="'input-' + componentId()"
        type="text"
        class="text-input"
        [class.input-error]="hasError()"
        [placeholder]="placeholder() || ''"
        [value]="value()"
        (input)="handleInput($event)"
      />
      @if (hasError()) {
        <div class="error-container" data-testid="validation-errors">
          @for (err of validationErrors(); track $index) {
            <span class="error-msg">{{ err }}</span>
          }
        </div>
      }
    </div>
  `,
  styles: [
    `
      .input-group {
        display: flex;
        flex-direction: column;
        gap: 6px;
      }
      .input-label {
        font-size: 0.875rem;
        font-weight: 500;
        color: #334155;
      }
      .text-input {
        padding: 8px 12px;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        font-size: 0.95rem;
        outline: none;
        transition: border-color 0.15s ease;
      }
      .text-input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
      }
      .text-input.input-error {
        border-color: #ef4444;
        background-color: #fef2f2;
      }
      .error-container {
        display: flex;
        flex-direction: column;
        gap: 2px;
      }
      .error-msg {
        font-size: 0.8rem;
        color: #dc2626;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SmartInputComponent extends CatalogComponent<typeof SmartInputApi> {
  readonly label = computed(() => this.props()['label']?.value() || 'Input');
  readonly placeholder = computed(() => this.props()['placeholder']?.value());
  readonly value = computed(() => {
    const raw = this.props()['value']?.value();
    return raw !== undefined && raw !== null ? String(raw) : '';
  });
  readonly validationErrors = computed(() => {
    const errors = this.props()['validationErrors']?.value();
    return Array.isArray(errors) ? (errors as string[]) : [];
  });
  readonly hasError = computed(() => this.validationErrors().length > 0);

  handleInput(event: Event) {
    const val = (event.target as HTMLInputElement).value;
    this.props()['value']?.onUpdate(val);
  }
}
