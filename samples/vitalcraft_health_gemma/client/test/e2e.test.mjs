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

import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import puppeteer from 'puppeteer-core';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const screenshotsDir = path.resolve(__dirname, '../screenshots');

if (!fs.existsSync(screenshotsDir)) {
  fs.mkdirSync(screenshotsDir, {recursive: true});
}

const CHROME_PATH =
  process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const APP_URL = process.env.APP_URL || 'http://127.0.0.1:8000';

console.log('🚀 Starting VitalCraft E2E Puppeteer verification...');
console.log(`- Chrome binary: ${CHROME_PATH}`);
console.log(`- Target URL: ${APP_URL}`);

async function run() {
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,960'],
  });

  try {
    const page = await browser.newPage();
    await page.setViewport({width: 1280, height: 960});

    page.on('console', msg => console.log(`   [Browser] ${msg.type()}: ${msg.text()}`));
    page.on('pageerror', err => console.error(`   [Browser Error]:`, err));

    console.log('1. Navigating to VitalCraft app...');
    await page.goto(APP_URL, {waitUntil: 'networkidle0', timeout: 15000});

    // Verify Header
    await page.waitForSelector('.app-header', {timeout: 5000});
    const headerTitle = await page.$eval('.header-title-group h1', el => el.textContent);
    console.log(`   Header title: "${headerTitle}"`);
    if (!headerTitle?.includes('VitalCraft')) {
      throw new Error(`Unexpected header title: ${headerTitle}`);
    }

    // Verify Welcome message
    await page.waitForSelector('.bubble-assistant', {timeout: 5000});
    console.log('   Welcome message verified.');

    // Find and click the first quick prompt chip
    console.log('2. Triggering prompt: "Show my recent blood pressure logs and 7-day trend"...');
    await page.waitForSelector('.mcq-chip', {timeout: 5000});
    const chips = await page.$$('.mcq-chip');
    if (chips.length === 0) {
      throw new Error('No quick prompt chips found');
    }
    await chips[0].click();

    // Wait for the assistant's turn response to stream and render custom A2UI components
    console.log('3. Waiting for A2UI components to render on the surface...');
    await page.waitForSelector('.bp-card', {timeout: 60000});
    await page.waitForSelector('.trend-chart-card', {timeout: 60000});
    await page.waitForSelector('svg line', {timeout: 15000});

    // Validate rendered component data
    const bpText = await page.$eval('.bp-card .bp-number', el => el.textContent);
    const chartTitle = await page.$eval('.trend-chart-card .chart-title', el => el.textContent);
    console.log(`   Rendered BP Reading: ${bpText} mmHg`);
    console.log(`   Rendered Chart Title: "${chartTitle}"`);

    // Wait for the full turn stream to complete
    console.log('   Waiting for turn stream completion...');
    await page.waitForFunction(() => !document.querySelector('.chat-input')?.disabled, {
      timeout: 60000,
    });
    await new Promise(r => setTimeout(r, 600));

    // Capture first screenshot: Completed turn with cards and charts
    const chatScreenshotPath = path.join(screenshotsDir, 'vitalcraft_e2e.png');
    await page.screenshot({path: chatScreenshotPath, fullPage: false});
    console.log(`📸 Screenshot saved: ${chatScreenshotPath}`);

    // Test Turn 2: Follow-up interactive prompt or chip selection
    console.log(
      '4. Testing Turn 2 (multi-turn rendering): Proposing a 2-week cardiovascular workout plan...',
    );
    const inputSelector = '.chat-input';
    await page.waitForSelector(inputSelector, {timeout: 5000});
    await page.type(inputSelector, 'Build a workout plan to lower BP');
    await page.keyboard.press('Enter');

    console.log('   Waiting for Turn 2 generative UI components to render...');
    await page.waitForSelector('.plan-card, .habit-card', {timeout: 60000});
    await page.waitForFunction(() => !document.querySelector('.chat-input')?.disabled, {
      timeout: 60000,
    });
    await new Promise(r => setTimeout(r, 600));

    const planTitle = await page
      .$eval('.plan-card .plan-title', el => el.textContent)
      .catch(() => 'Habit Tracker');
    console.log(`   Turn 2 Rendered Component Title: "${planTitle}"`);

    // Capture second screenshot: Multi-turn chat with plan builder
    const multiTurnScreenshotPath = path.join(screenshotsDir, 'vitalcraft_multi_turn_e2e.png');
    await page.screenshot({path: multiTurnScreenshotPath, fullPage: false});
    console.log(`📸 Multi-Turn Screenshot saved: ${multiTurnScreenshotPath}`);

    // Click the info button on the assistant turn to open the Syntax Inspector drawer
    console.log('5. Clicking "ℹ️ Format Details" to open format inspector drawer...');
    const infoButtons = await page.$$('.info-btn');
    if (infoButtons.length > 0) {
      await infoButtons[infoButtons.length - 1].click();
      await page.waitForSelector('.inspector-drawer', {timeout: 5000});
      await page.waitForSelector('.code-block', {timeout: 5000});

      const verticalCode = await page.$eval('.code-block code', el => el.textContent);
      console.log(`   Vertical DSL snippet preview:\n${verticalCode?.slice(0, 160)}...`);

      // Capture screenshot: Vertical DSL Tab
      const verticalScreenshotPath = path.join(screenshotsDir, 'vitalcraft_vertical_dsl_e2e.png');
      await page.screenshot({path: verticalScreenshotPath, fullPage: false});
      console.log(`📸 Vertical DSL Screenshot saved: ${verticalScreenshotPath}`);

      // Switch to A2UI wire tab
      const tabs = await page.$$('.inspector-tab');
      if (tabs.length > 1) {
        await tabs[1].click();
        await new Promise(r => setTimeout(r, 500));
      }

      // Capture screenshot: Inspector Drawer Wire JSON Tab
      const inspectorScreenshotPath = path.join(screenshotsDir, 'vitalcraft_inspector_e2e.png');
      await page.screenshot({path: inspectorScreenshotPath, fullPage: false});
      console.log(`📸 Inspector Wire JSON Screenshot saved: ${inspectorScreenshotPath}`);
    } else {
      console.warn('⚠️ No info button found');
    }

    console.log('✅ VitalCraft E2E Puppeteer verification completed successfully!');
  } finally {
    await browser.close();
  }
}

run().catch(err => {
  console.error('❌ E2E test failed:', err);
  process.exit(1);
});
