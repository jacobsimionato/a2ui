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

import React from 'react';
import {A2uiSurface, type ReactComponentImplementation} from '@a2ui/react/v0_9';
import type {SurfaceModel} from '@a2ui/web_core/v0_9';
import type {ChatMessage} from '../types';

interface MessageBubbleProps {
  message: ChatMessage;
  surfaces: SurfaceModel<ReactComponentImplementation>[];
  onInspect: (message: ChatMessage) => void;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({message, surfaces, onInspect}) => {
  const isUser = message.role === 'user';

  if (isUser) {
    return (
      <div className="message-turn user">
        <div className="bubble-user">{message.text}</div>
      </div>
    );
  }

  return (
    <div className="message-turn assistant">
      <div className="turn-meta-header">
        <span>🤖 {message.model || 'Gemma 2B'}</span>
        {message.latencySec !== undefined && (
          <span className="latency-pill">⚡ {message.latencySec}s</span>
        )}
        <button
          type="button"
          className="info-btn"
          onClick={() => onInspect(message)}
          title="Inspect Vertical Format & Protocol Wire JSON"
        >
          ℹ️ Format Details
        </button>
      </div>

      <div className="bubble-assistant">
        {message.text && <div className="assistant-text">{message.text}</div>}

        {surfaces.length > 0 && (
          <div className="surfaces-stack">
            {surfaces.map(surface => (
              <A2uiSurface key={surface.id} surface={surface} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
