// ***********************************************************
// This example support/index.js is processed and
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
import "@cypress/code-coverage/support"

Cypress.on("window:before:load", (win) => {
  cy.spy(win.console, "info").as("consoleInfo")
  cy.stub(win.console, "warn")
    .as("consolWarn")
    .callsFake((message) => {
      if (message.startsWith("[Vue warn]")) {
        const allowedMessages = [
          '[Vue warn]: Invalid event arguments: event validation failed for event "',
          "[Vue warn]: Extraneous non-props attributes"
        ]
        for (const allowedMessage of allowedMessages) {
          if (message.startsWith(allowedMessage)) return
        }
        throw new SyntaxError(message)
      }
    })
})

Cypress.on("uncaught:exception", (err) => {
  if (err.message.includes("Element provided to #addTo() exists, but is not in the DOM")) {
    return false
  }
  return true
})
