/// <reference types="cypress" />
import { defineComponent, h, withDirectives, resolveDirective } from "vue"

const TooltipButton = defineComponent({
  setup: () => () =>
    withDirectives(h("button", { "data-cy": "target", type: "button" }, "Cible"), [
      [resolveDirective("tooltip")!, "Infobulle"]
    ])
})

describe("v-tooltip", () => {
  beforeEach(() => {
    cy.mount(TooltipButton)
  })

  it("shows on mouse hover and hides when the mouse leaves", () => {
    cy.getBySel("target").trigger("pointerenter", { pointerType: "mouse" })
    cy.get("[role=tooltip]").should("contain.text", "Infobulle")

    cy.getBySel("target").trigger("pointerleave", { pointerType: "mouse" })
    cy.get("[role=tooltip]").should("not.exist")
  })

  it("stays hidden after a tap, which never sends the leave events", () => {
    // cy.click() simulates a mouse, hover included: replay a tap's pointer events instead.
    cy.getBySel("target")
      .trigger("pointerenter", { pointerType: "touch" })
      .trigger("mouseenter")
      .trigger("click")

    cy.get("[role=tooltip]").should("not.exist")
  })
})
