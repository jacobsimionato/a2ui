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

import {bootstrapApplication} from '@angular/platform-browser';
import {provideZonelessChangeDetection} from '@angular/core';
import {provideA2Ui} from '@a2ui/angular/v0_9';
import {AppComponent} from './app/app';
import {CommonCatalogV09, CommonCatalogV10, ExtensionCatalogV10} from './app/catalogs/catalogs';

bootstrapApplication(AppComponent, {
  providers: [
    provideZonelessChangeDetection(),
    provideA2Ui({
      catalogs: [new CommonCatalogV09(), new CommonCatalogV10(), new ExtensionCatalogV10()],
    }),
  ],
}).catch(err => console.error('Bootstrap error:', err));
