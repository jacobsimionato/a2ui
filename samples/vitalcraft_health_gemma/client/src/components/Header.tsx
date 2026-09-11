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
import type {ServerStatus} from '../types';

interface HeaderProps {
  status: ServerStatus | null;
}

export const Header: React.FC<HeaderProps> = ({status}) => {
  const isOllama = status?.ollama_available;
  const modelName = status?.model || 'Gemma 2B (On-Device)';

  return (
    <header className="app-header">
      <div className="header-brand">
        <div className="header-logo">❤️</div>
        <div className="header-title-group">
          <h1>VitalCraft</h1>
          <div className="header-subtitle">
            Private On-Device Health Assistant • A2UI Vertical Format
          </div>
        </div>
      </div>

      <div className="header-badge">
        <div className="status-dot" />
        <span>{isOllama ? `Ollama: ${modelName}` : `${modelName}`}</span>
      </div>
    </header>
  );
};
