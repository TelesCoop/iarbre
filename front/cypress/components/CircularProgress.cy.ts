import CircularProgress from "@/components/progress/CircularProgress.vue"

describe("CircularProgress.vue", () => {
  it("renders with default props", () => {
    cy.mount(CircularProgress, {
      props: {
        percentage: 50
      }
    })

    cy.get("svg").should("exist")
    cy.get("svg").should("have.attr", "role", "img")
    cy.get("circle").should("have.length", 2)
  })

  it("renders with 0% progress", () => {
    cy.mount(CircularProgress, {
      props: {
        percentage: 0
      }
    })

    cy.get("svg").should("exist")
    cy.get("circle").should("have.length", 2)
  })

  it("renders with 100% progress", () => {
    cy.mount(CircularProgress, {
      props: {
        percentage: 100
      }
    })

    cy.get("svg").should("exist")
    cy.get("circle").should("have.length", 2)
  })

  it("renders with custom strokeWidth", () => {
    cy.mount(CircularProgress, {
      props: {
        percentage: 75,
        strokeWidth: 12
      }
    })

    cy.get("circle").first().should("have.attr", "stroke-width", "12")
  })

  it("renders with custom backgroundColor", () => {
    cy.mount(CircularProgress, {
      props: {
        percentage: 60,
        backgroundColor: "text-blue-500"
      }
    })

    cy.get("circle").eq(1).should("have.class", "text-blue-500")
  })
})
