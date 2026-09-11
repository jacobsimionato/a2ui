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

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  text: string;
  surfaceIds: string[];
  wireMessages: A2uiMessage[];
  rawVertical: string;
  latencySec?: number;
  model?: string;
  timestamp: string;
}

export interface ServerStatus {
  ollama_available: boolean;
  model: string | null;
  sample_app: string;
  protocol: string;
  inference_format: string;
}
