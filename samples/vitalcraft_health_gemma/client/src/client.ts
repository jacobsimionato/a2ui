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

import type {A2uiMessage} from '@a2ui/web_core/v0_9';
import type {ServerStatus} from './types';

export interface StreamEvent {
  type: 'text' | 'a2ui_wire' | 'metadata';
  content?: string;
  messages?: A2uiMessage[];
  model?: string;
  latency_sec?: number;
  tokens?: number;
  raw_vertical?: string;
  elapsed?: number;
}

export async function fetchStatus(): Promise<ServerStatus> {
  try {
    const res = await fetch('/api/status');
    if (!res.ok) throw new Error(`Status HTTP ${res.status}`);
    return await res.json();
  } catch (_err) {
    return {
      ollama_available: false,
      model: null,
      sample_app: 'VitalCraft Health (Offline Fallback)',
      protocol: 'v0.9.1',
      inference_format: 'vertical',
    };
  }
}

export async function streamChat(
  message: string,
  history: Array<{role: string; content: string}>,
  onEvent: (event: StreamEvent) => void,
): Promise<void> {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({message, history}),
  });

  if (!response.ok) {
    throw new Error(`Chat API error: HTTP ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('No response body stream');
  }

  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const {done, value} = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, {stream: true});
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith(':')) continue;

      if (trimmed.startsWith('data: ')) {
        const payload = trimmed.slice(6);
        if (payload === '[DONE]') {
          return;
        }
        try {
          const parsed = JSON.parse(payload) as StreamEvent;
          onEvent(parsed);
        } catch (e) {
          console.error('Failed to parse SSE line:', line, e);
        }
      }
    }
  }
}
