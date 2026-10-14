/// <reference types="cypress" />
import { defineComponent, h, ref, withDirectives } from "vue"
import { vTooltip } from "@/directives/tooltip"

type Position = "top" | "bottom" | "left" | "right"

const text = ref("Aide")
const isShown = ref(true)

const mountWithTooltip = (position?: Position) => {
  text.value = "Aide"
  isShown.value = true
  const modifiers = position ? { [position]: true } : {}
  const Host = defineComponent({
    setup: () => () =>
      h("div", { style: "padding: 200px" }, [
        isShown.value
          ? withDirectives(h("button", { "data-cy": "target" }, "Cible"), [
              [vTooltip, text.value, "", modifiers]
            ])
          : null
      ])
  })
  return cy.mount(Host)
}

const pointer = (type: "pointerenter" | "pointerleave", pointerType = "mouse") =>
  cy.getBySel("target").trigger(type, { pointerType })

const expectNoTooltip = () => cy.get("[role=tooltip]").should("not.exist")

describe("vTooltip", () => {
  it("shows the tooltip on top when a mouse enters, and removes it when it leaves", () => {
    mountWithTooltip()
    pointer("pointerenter")

    cy.get("[role=tooltip]")
      .should("have.class", "visible")
      .and("have.class", "app-tooltip-top")
      .and("have.text", "Aide")
    cy.get("[role=tooltip]").then(($tooltip) => {
      cy.getBySel("target").then(($target) => {
        const tooltip = $tooltip[0].getBoundingClientRect()
        expect(tooltip.bottom).to.be.at.most($target[0].getBoundingClientRect().top)
      })
    })

    pointer("pointerleave")
    expectNoTooltip()
  })

  it("shows the tooltip for a pen", () => {
    mountWithTooltip()
    pointer("pointerenter", "pen")
    cy.get("[role=tooltip]").should("have.class", "visible")
  })

  it("ignores a tap, which never sends the leave events", () => {
    mountWithTooltip()
    pointer("pointerenter", "touch")
    cy.wait(50)
    expectNoTooltip()
  })

  it("shows the tooltip on keyboard focus and removes it on blur", () => {
    mountWithTooltip()
    cy.getBySel("target").focus()
    cy.get("[role=tooltip]").should("have.class", "visible")

    cy.getBySel("target").blur()
    expectNoTooltip()
  })

  it("keeps a single tooltip when shown twice", () => {
    mountWithTooltip()
    pointer("pointerenter")
    pointer("pointerenter")
    cy.get("[role=tooltip]").should("have.length", 1)
  })

  const sides: [Position, (tooltip: DOMRect, target: DOMRect) => void][] = [
    ["bottom", (tooltip, target) => expect(tooltip.top).to.be.at.least(target.bottom)],
    ["left", (tooltip, target) => expect(tooltip.right).to.be.at.most(target.left)],
    ["right", (tooltip, target) => expect(tooltip.left).to.be.at.least(target.right)]
  ]
  sides.forEach(([position, expectSide]) => {
    it(`places the tooltip on the ${position}`, () => {
      mountWithTooltip(position)
      pointer("pointerenter")

      cy.get("[role=tooltip]")
        .should("have.class", "visible")
        .and("have.class", `app-tooltip-${position}`)
        .then(($tooltip) => {
          cy.getBySel("target").then(($target) => {
            expectSide($tooltip[0].getBoundingClientRect(), $target[0].getBoundingClientRect())
          })
        })
    })
  })

  it("shows the updated text", () => {
    mountWithTooltip()
    cy.then(() => {
      text.value = "Nouvelle aide"
    })
    pointer("pointerenter")
    cy.get("[role=tooltip]").should("have.text", "Nouvelle aide")
  })

  it("removes the open tooltip when the element is unmounted", () => {
    mountWithTooltip()
    pointer("pointerenter")
    cy.get("[role=tooltip]").should("exist")

    cy.then(() => {
      isShown.value = false
    })
    expectNoTooltip()
  })

  it("does nothing without a text", () => {
    mountWithTooltip()
    cy.then(() => {
      text.value = ""
      isShown.value = false
    })
    cy.then(() => {
      isShown.value = true
    })
    pointer("pointerenter")
    cy.wait(50)
    expectNoTooltip()
  })
})
