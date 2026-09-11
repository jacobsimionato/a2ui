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

import {useState} from 'react';
import type {ChatMessage} from '../types';

interface SyntaxInspectorProps {
  message: ChatMessage | null;
  onClose: () => void;
}

export function SyntaxInspector({message, onClose}: SyntaxInspectorProps) {
  const [activeTab, setActiveTab] = useState<'vertical' | 'a2ui'>('vertical');

  if (!message) return null;

  const wireJsonString = message.wireMessages?.length
    ? JSON.stringify(message.wireMessages, null, 2)
    : '/* No A2UI protocol wire messages received for this turn */';

  const verticalCode =
    message.rawVertical || '/* No raw Vertical DSL emitted or plain conversational text turn */';

  return (
    <div className="inspector-overlay" onClick={onClose}>
      <div className="inspector-drawer" onClick={e => e.stopPropagation()}>
        <div className="inspector-header">
          <div>
            <h2>Format Inspector & Telemetry</h2>
            <div style={{fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px'}}>
              Model:{' '}
              <span style={{color: 'var(--text-primary)'}}>{message.model || 'Gemma 2B'}</span> •{' '}
              Latency:{' '}
              <span style={{color: 'var(--accent-teal)'}}>
                {message.latencySec ? `${message.latencySec}s` : 'N/A'}
              </span>
            </div>
          </div>
          <button type="button" className="close-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="inspector-tabs">
          <button
            type="button"
            className={`inspector-tab ${activeTab === 'vertical' ? 'active' : ''}`}
            onClick={() => setActiveTab('vertical')}
          >
            Vertical DSL (Model Output)
          </button>
          <button
            type="button"
            className={`inspector-tab ${activeTab === 'a2ui' ? 'active' : ''}`}
            onClick={() => setActiveTab('a2ui')}
          >
            Compiled A2UI JSON (Wire Protocol)
          </button>
        </div>

        <div className="inspector-content">
          {activeTab === 'vertical' ? (
            <div>
              <div
                style={{
                  fontSize: '11.5px',
                  color: 'var(--text-muted)',
                  marginBottom: '10px',
                  lineHeight: 1.4,
                }}
              >
                💡 The concise <strong>Vertical inference format</strong> uses positional arguments
                and indentation, saving ~70% of tokens compared to verbose JSON schemas on
                constrained on-device models.
              </div>
              <pre className="code-block">
                <code>{verticalCode}</code>
              </pre>
            </div>
          ) : (
            <div>
              <div
                style={{
                  fontSize: '11.5px',
                  color: 'var(--text-muted)',
                  marginBottom: '10px',
                  lineHeight: 1.4,
                }}
              >
                📡 The compiled <strong>A2UI v0.9.1 JSON protocol messages</strong> delivered to the
                web client and processed by the A2UI Surface engine:
              </div>
              <pre className="code-block">
                <code>{wireJsonString}</code>
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
