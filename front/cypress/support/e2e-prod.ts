import "./commands"

beforeEach(() => {
  cy.setCookie("tarteaucitron", "!matomo=false")
})

Cypress.on("window:before:load", (win) => {
  win.localStorage.setItem("hasVisitedBefore", "true")
  cy.spy(win.console, "info").as("consoleInfo")
})
