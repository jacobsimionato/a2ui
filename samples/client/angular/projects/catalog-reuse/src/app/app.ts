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

import {ChangeDetectionStrategy, Component, OnInit, inject, signal} from '@angular/core';
import {CommonModule} from '@angular/common';
import {A2uiRendererService, SurfaceComponent} from '@a2ui/angular/v0_9';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, SurfaceComponent],
  templateUrl: './app.html',
  styleUrl: './app.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AppComponent implements OnInit {
  protected renderer = inject(A2uiRendererService);

  readonly activeTab = signal<'all' | 'v09' | 'v10'>('all');
  readonly isLoaded = signal(false);
  readonly errorMessage = signal<string | null>(null);
  readonly dispatchedActions = signal<string[]>([]);

  ngOnInit() {
    this.renderer.surfaceGroup.onAction.subscribe(action => {
      const logEntry = `[${new Date().toLocaleTimeString()}] Action dispatched: ${JSON.stringify(action)}`;
      this.dispatchedActions.update(prev => [logEntry, ...prev]);
    });

    void this.loadPayloads();
  }

  async loadPayloads() {
    try {
      // 1. Fetch and process v0.9 payload
      const v09Resp = await fetch('/api/v0_9');
      if (!v09Resp.ok) throw new Error(`Failed to fetch v0.9 payload: ${v09Resp.statusText}`);
      const v09Messages = await v09Resp.json();
      await this.renderer.processMessagesAsync(v09Messages);

      // 2. Fetch and process v1.0 payload
      const v10Resp = await fetch('/api/v1_0');
      if (!v10Resp.ok) throw new Error(`Failed to fetch v1.0 payload: ${v10Resp.statusText}`);
      const v10Messages = await v10Resp.json();
      await this.renderer.processMessagesAsync(v10Messages);

      this.isLoaded.set(true);
    } catch (err: unknown) {
      console.error('Error loading A2UI content:', err);
      this.errorMessage.set(err instanceof Error ? err.message : String(err));
    }
  }

  setTab(tab: 'all' | 'v09' | 'v10') {
    this.activeTab.set(tab);
  }
}
