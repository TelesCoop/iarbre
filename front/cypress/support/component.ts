// ***********************************************************
// This example support/component.ts is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

import "./commands"

// Import coverage support
import "@cypress/code-coverage/support"

import "@/styles/main.css"
import { createPinia } from "pinia"
import { vTooltip } from "@/directives/tooltip"

import { mount } from "cypress/vue"

beforeEach(() => {
  cy.window()
    .its("console")
    .then((console) => {
      cy.stub(console, "warn")
        .as("onConsoleWarn")
        .callsFake((message) => {
          if (message.startsWith("[Vue warn]")) {
            const allowedMessages = [
              '[Vue warn]: Invalid event arguments: event validation failed for event "',
              "[Vue warn]: Wrong type passed as event handler to",
              "[Vue warn]: Extraneous non-props attributes",
              "[Vue warn]: Failed to resolve component: Chart"
            ]
            for (const allowedMessage of allowedMessages) {
              if (message.startsWith(allowedMessage)) return
            }
            throw new SyntaxError(message)
          }
        })
    })
})
afterEach(() => {
  cy.get("@onConsoleWarn").should("have.not.thrown", SyntaxError)
})

// Augment the Cypress namespace to include type definitions for
// your custom command.
// Alternatively, can be defined in cypress/support/component.d.ts
// with a <reference path="./component" /> at the top of your spec.
declare global {
  namespace Cypress {
    interface Chainable {
      mount: typeof mount
    }
  }
}

Cypress.Commands.add("mount", (component, options) => {
  // Setup options object
  if (!options) {
    options = {}
  }
  options.global = options.global || {}
  options.global.plugins = options?.global.plugins || []
  options.global.directives = options?.global.directives || {}
  options.global.plugins.push({
    install(app) {
      app.use(createPinia())
      app.directive("tooltip", vTooltip)
    }
  })

  return mount(component, options)
})
