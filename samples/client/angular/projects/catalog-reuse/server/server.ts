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

import express from 'express';
import path from 'node:path';
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
import {V09_PAYLOAD} from './payloads/payload_v0_9.js';
import {V10_PAYLOAD} from './payloads/payload_v1_0.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = Number(process.env.PORT) || 4205;

app.use(express.json());

// 1. Catalog JSON Schema Endpoints
app.get('/catalogs/common/v0_9/catalog.json', (_req, res) => {
  const filePath = path.join(__dirname, 'schemas', 'catalog_v0_9.json');
  res.sendFile(filePath);
});

app.get('/catalogs/common/v1_0/catalog.json', (_req, res) => {
  const filePath = path.join(__dirname, 'schemas', 'catalog_v1_0.json');
  res.sendFile(filePath);
});

app.get('/catalogs/v1_extension/catalog.json', (_req, res) => {
  const filePath = path.join(__dirname, 'schemas', 'catalog_v1_extension.json');
  res.sendFile(filePath);
});

// 2. Dummy Constant A2UI Content Endpoints
app.get('/api/v0_9', (_req, res) => {
  res.json(V09_PAYLOAD);
});

app.get('/api/v1_0', (_req, res) => {
  res.json(V10_PAYLOAD);
});

// 3. Static Client Hosting
const distDirs = [path.join(__dirname, '../dist/browser'), path.join(__dirname, '../dist')];
const distPath = distDirs.find(d => fs.existsSync(d)) || distDirs[0];

if (fs.existsSync(distPath)) {
  app.use(express.static(distPath));
  app.use((_req, res) => {
    res.sendFile(path.join(distPath, 'index.html'));
  });
} else {
  app.use((_req, res) => {
    res.send('A2UI Server running. Build the frontend (`yarn build`) to serve UI.');
  });
}

const server = app.listen(PORT, () => {
  console.log(`[A2UI TS Server] Running on http://localhost:${PORT}`);
});

export {app, server};
