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

// Import commands.js using ES2015 syntax:
import "./commands"

import "@/styles/main.css"

// Alternatively you can use CommonJS syntax:
// require('./commands')

import { mount } from "cypress/vue"

beforeEach(() => {
  cy.window()
    .its("console")
    .then((console) => {
      cy.stub(console, "warn")
        .as("onConsoleWarn")
        .callsFake((message) => {
          console.log
          if (message.startsWith("[Vue warn]")) {
            const allowedMessages = [
              '[Vue warn]: Invalid event arguments: event validation failed for event "'
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
  cy.get("@onConsoleWarn").should("have.have.not.thrown", SyntaxError)
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

Cypress.Commands.add("mount", mount)

// Example use:
// cy.mount(MyComponent)
