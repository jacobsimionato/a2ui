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

export const V09_PAYLOAD = {
  version: 'v0.9',
  messages: [
    {
      version: 'v0.9',
      createSurface: {
        surfaceId: 'v09-demo-surface',
        catalogId: 'https://example.com/catalogs/common/v0_9/catalog.json',
      },
    },
    {
      version: 'v0.9',
      updateDataModel: {
        surfaceId: 'v09-demo-surface',
        path: '/',
        value: {
          customer: {
            name: 'Jane Doe',
          },
          order: {
            priority: 4,
          },
          cart: {
            items: [
              {name: 'Premium Cloud Widget'},
              {name: 'Universal Power Adapter'},
              {name: 'High-Speed USB-C Cable'},
            ],
          },
        },
      },
    },
    {
      version: 'v0.9',
      updateComponents: {
        surfaceId: 'v09-demo-surface',
        components: [
          {
            id: 'root',
            component: 'ContainerCard',
            title: 'Order Review (v0.9 Protocol)',
            subtitle: 'Demonstrating Shared Angular Catalog Components in v0.9',
            badge: 'v0.9 Active',
            children: ['detailsCard', 'summaryCard', 'cartCard', 'submitBtn'],
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
            placeholder: 'e.g. Jane Doe',
            value: {path: '/customer/name'},
            checks: [
              {
                condition: {
                  call: 'checkRequired',
                  args: {value: {path: '/customer/name'}},
                },
                message: 'Customer name is required',
              },
            ],
          },
          {
            id: 'prioritySlider',
            component: 'RatingSlider',
            label: 'Order Priority / Quantity',
            min: 1,
            max: 10,
            value: {path: '/order/priority'},
          },
          {
            id: 'summaryCard',
            component: 'ComputedSummary',
            title: 'Calculated Order Pricing',
            greeting: {
              call: 'formatGreeting',
              args: {name: {path: '/customer/name'}},
            },
            total: {
              call: 'calculateTotal',
              args: {
                quantity: {path: '/order/priority'},
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
            text: {path: 'name'},
            variant: 'info',
          },
          {
            id: 'submitBtn',
            component: 'ActionTrigger',
            label: 'Submit Order (v0.9)',
            variant: 'primary',
            action: {
              event: {
                name: 'submitOrder',
                context: {
                  customer: {path: '/customer/name'},
                  priority: {path: '/order/priority'},
                },
              },
            },
          },
        ],
      },
    },
  ],
};
