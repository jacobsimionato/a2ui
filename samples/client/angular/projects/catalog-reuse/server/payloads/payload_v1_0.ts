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

export const V10_PAYLOAD = {
  version: 'v1.0',
  messages: [
    {
      version: 'v1.0',
      createSurface: {
        surfaceId: 'v10-demo-surface',
        catalogId: 'https://example.com/catalogs/common/v1_0/catalog.json',
      },
    },
    {
      version: 'v1.0',
      updateDataModel: {
        surfaceId: 'v10-demo-surface',
        path: '/',
        value: {
          customer: {
            name: 'John Smith',
          },
          order: {
            priority: 6,
            satisfaction: 85,
          },
          cart: {
            items: [{name: 'Enterprise AI Cluster'}, {name: 'Dedicated Fiber Interconnect'}],
          },
        },
      },
    },
    {
      version: 'v1.0',
      updateComponents: {
        surfaceId: 'v10-demo-surface',
        components: [
          {
            id: 'root',
            component: 'ContainerCard',
            title: 'Order Review (v1.0 Protocol)',
            subtitle: 'Demonstrating Shared Components + Mixed v1.0 Catalog Extension',
            badge: 'v1.0 Active',
            children: ['detailsCard', 'gaugeCard', 'summaryCard', 'cartCard', 'submitBtn'],
          },
          {
            id: 'detailsCard',
            component: 'ContainerCard',
            title: 'Customer & Preferences',
            children: ['customerInput', 'prioritySlider'],
          },
          {
            id: 'customerInput',
            component: 'SmartInput',
            label: 'Customer Full Name',
            placeholder: 'e.g. John Smith',
            value: {'@path': '/customer/name'},
            checks: [
              {
                condition: {
                  '@call': 'checkRequiredV1',
                  args: {value: {'@path': '/customer/name'}},
                },
              },
            ],
          },
          {
            id: 'prioritySlider',
            component: 'RatingSlider',
            label: 'Order Priority / Quantity',
            min: 1,
            max: 10,
            value: {'@path': '/order/priority'},
          },
          {
            id: 'gaugeCard',
            component: 'MetricGauge',
            // MULTI-CATALOG EXTENSION: References component from the v1.0 extension catalog!
            catalogId: 'https://example.com/catalogs/v1_extension/catalog.json',
            label: 'Customer SLA Satisfaction Index',
            score: {'@path': '/order/satisfaction'},
            maxScore: 100,
            trend: 'up',
          },
          {
            id: 'summaryCard',
            component: 'ComputedSummary',
            title: 'Calculated Order Pricing',
            greeting: {
              '@call': 'formatGreeting',
              args: {name: {'@path': '/customer/name'}},
            },
            total: {
              '@call': 'calculateTotal',
              args: {
                quantity: {'@path': '/order/priority'},
                unitPrice: 25,
              },
            },
          },
          {
            id: 'cartCard',
            component: 'DynamicRepeater',
            title: 'Items in Cart',
            children: {
              path: '/cart/items',
              componentId: 'cartBadgeTemplate',
            },
          },
          {
            id: 'cartBadgeTemplate',
            component: 'StatusBadge',
            text: {'@path': 'name'},
            variant: 'success',
          },
          {
            id: 'submitBtn',
            component: 'ActionTrigger',
            label: 'Submit Order (v1.0)',
            variant: 'primary',
            action: {
              event: {
                name: 'submitOrder',
                context: {
                  customer: {'@path': '/customer/name'},
                  priority: {'@path': '/order/priority'},
                },
              },
            },
          },
        ],
      },
    },
  ],
};
