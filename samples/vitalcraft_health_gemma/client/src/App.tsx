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

import {useState, useEffect, useMemo, useRef} from 'react';
import {basicCatalog, MarkdownContext, type ReactComponentImplementation} from '@a2ui/react/v0_9';
import {MessageProcessor, type SurfaceModel} from '@a2ui/web_core/v0_9';
import {renderMarkdown} from '@a2ui/markdown-it';

import {vitalcraftCatalog} from './catalog';
import {Header} from './components/Header';
import {MessageBubble} from './components/MessageBubble';
import {SyntaxInspector} from './components/SyntaxInspector';
import {fetchStatus, streamChat} from './client';
import type {ChatMessage, ServerStatus} from './types';
import './App.css';

const QUICK_PROMPTS = [
  'Show my recent blood pressure logs and 7-day trend',
  'Compare my vitals and propose a 2-week cardiovascular workout plan',
  'What daily heart-health habits should I focus on?',
];

export function App() {
  const [status, setStatus] = useState<ServerStatus | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      role: 'assistant',
      text: "👋 Welcome to **VitalCraft**, your 100% private, on-device health assistant powered by Google's Gemma 2B model and the compact A2UI Vertical inference format.\n\nAll your blood pressure readings, exercise metrics, and health goals remain strictly private on this machine. How can I assist you today?",
      surfaceIds: [],
      wireMessages: [],
      rawVertical: '',
      model: 'Gemma 2B (On-Device)',
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [requesting, setRequesting] = useState(false);
  const [selectedTurnForInspector, setSelectedTurnForInspector] = useState<ChatMessage | null>(
    null,
  );
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // Initialize A2UI MessageProcessor with basicCatalog and custom vitalcraftCatalog
  const processor = useMemo(() => {
    return new MessageProcessor<ReactComponentImplementation>(
      [basicCatalog, vitalcraftCatalog],
      action => {
        console.log('A2UI Client Action:', action);
      },
    );
  }, []);

  // Track active surfaces for reactive rendering
  const [, setSurfaceRevision] = useState(0);

  useEffect(() => {
    const sub1 = processor.onSurfaceCreated(() => {
      setSurfaceRevision(r => r + 1);
    });
    const sub2 = processor.onSurfaceDeleted(() => {
      setSurfaceRevision(r => r + 1);
    });
    return () => {
      sub1.unsubscribe();
      sub2.unsubscribe();
    };
  }, [processor]);

  // Load server status on mount
  useEffect(() => {
    fetchStatus().then(setStatus);
  }, []);

  // Auto-scroll on message updates
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({behavior: 'smooth'});
  }, [messages, requesting]);

  const handleSendRef = useRef<(text?: string) => Promise<void>>(async () => {});

  useEffect(() => {
    const handleChoice = (e: Event) => {
      const customEvent = e as CustomEvent<{question: string; option: string}>;
      if (customEvent.detail?.option) {
        handleSendRef.current(customEvent.detail.option);
      }
    };
    window.addEventListener('vitalcraft:choice-selected', handleChoice);
    return () => window.removeEventListener('vitalcraft:choice-selected', handleChoice);
  }, []);

  const handleSend = async (textToSend?: string) => {
    const prompt = (textToSend || inputText).trim();
    if (!prompt || requesting) return;

    setInputText('');
    setRequesting(true);

    const userMsgId = `user-${Date.now()}`;
    const userMsg: ChatMessage = {
      id: userMsgId,
      role: 'user',
      text: prompt,
      surfaceIds: [],
      wireMessages: [],
      rawVertical: '',
      timestamp: new Date().toLocaleTimeString(),
    };

    const assistantMsgId = `asst-${Date.now()}`;
    const assistantMsg: ChatMessage = {
      id: assistantMsgId,
      role: 'assistant',
      text: '',
      surfaceIds: [],
      wireMessages: [],
      rawVertical: '',
      model: status?.model || 'Gemma 2B',
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages(prev => [...prev, userMsg, assistantMsg]);

    const history = messages
      .filter(m => m.id !== 'welcome')
      .map(m => ({role: m.role, content: m.text}));

    try {
      await streamChat(prompt, history, event => {
        if (event.type === 'text' && event.content) {
          setMessages(prev =>
            prev.map(m => (m.id === assistantMsgId ? {...m, text: m.text + event.content} : m)),
          );
        } else if (event.type === 'a2ui_wire' && event.messages) {
          processor.processMessages(event.messages);

          // Find created surface IDs in this batch
          const surfaceIds: string[] = [];
          for (const msg of event.messages) {
            if ('createSurface' in msg && msg.createSurface?.surfaceId) {
              surfaceIds.push(msg.createSurface.surfaceId);
            }
          }

          setMessages(prev =>
            prev.map(m => {
              if (m.id === assistantMsgId) {
                const combinedWire = [...m.wireMessages, ...event.messages!];
                const combinedSurfaces = Array.from(new Set([...m.surfaceIds, ...surfaceIds]));
                return {
                  ...m,
                  wireMessages: combinedWire,
                  surfaceIds: combinedSurfaces,
                };
              }
              return m;
            }),
          );
        } else if (event.type === 'metadata') {
          setMessages(prev =>
            prev.map(m => {
              if (m.id === assistantMsgId) {
                return {
                  ...m,
                  model: event.model || m.model,
                  latencySec: event.latency_sec,
                  rawVertical: event.raw_vertical || m.rawVertical,
                };
              }
              return m;
            }),
          );
        }
      });
    } catch (err) {
      console.error('Chat error:', err);
      setMessages(prev =>
        prev.map(m =>
          m.id === assistantMsgId
            ? {...m, text: m.text + `\n\n*(Error streaming response: ${err})*`}
            : m,
        ),
      );
    } finally {
      setRequesting(false);
    }
  };

  useEffect(() => {
    handleSendRef.current = handleSend;
  }, [handleSend]);

  const getSurfacesForMessage = (msg: ChatMessage) => {
    if (msg.surfaceIds.length === 0) return [];
    return msg.surfaceIds
      .map(id => processor.model.surfacesMap.get(id))
      .filter((s): s is SurfaceModel<ReactComponentImplementation> => !!s);
  };

  return (
    <MarkdownContext.Provider value={renderMarkdown}>
      <div className="app-container">
        <Header status={status} />

        <main className="messages-container">
          {messages.map(msg => (
            <MessageBubble
              key={msg.id}
              message={msg}
              surfaces={getSurfacesForMessage(msg)}
              onInspect={turn => setSelectedTurnForInspector(turn)}
            />
          ))}

          {requesting && (
            <div className="message-turn assistant">
              <div className="turn-meta-header">
                <span>🤖 {status?.model || 'Gemma 2B'}</span>
                <span className="latency-pill">⚡ Generating on-device UI...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </main>

        <footer className="input-form-container">
          {messages.length <= 1 && (
            <div style={{display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '12px'}}>
              {QUICK_PROMPTS.map((prompt, i) => (
                <button
                  type="button"
                  key={i}
                  className="mcq-chip"
                  onClick={() => handleSend(prompt)}
                  disabled={requesting}
                  style={{fontSize: '12px', padding: '6px 12px'}}
                >
                  💡 {prompt}
                </button>
              ))}
            </div>
          )}

          <form
            className="chat-input-form"
            onSubmit={e => {
              e.preventDefault();
              handleSend();
            }}
          >
            <input
              type="text"
              className="chat-input"
              value={inputText}
              onChange={e => setInputText(e.target.value)}
              placeholder="Ask about blood pressure, exercises, or plan your goals..."
              disabled={requesting}
            />
            <button type="submit" className="send-btn" disabled={requesting || !inputText.trim()}>
              Send
            </button>
          </form>
        </footer>

        <SyntaxInspector
          message={selectedTurnForInspector}
          onClose={() => setSelectedTurnForInspector(null)}
        />
      </div>
    </MarkdownContext.Provider>
  );
}
