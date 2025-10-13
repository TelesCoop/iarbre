/// <reference types="cypress" />
import { createPinia } from "pinia"
import { mount } from "cypress/vue"
import ClimateContextDataMetrics from "@/components/contextData/climate/ClimateContextDataMetrics.vue"
import { ClimateZone } from "@/types/climate"

describe("ClimateContextDataMetrics", () => {
  it("renders with climate data", () => {
    const pinia = createPinia()
    const mockData = {
      zone: ClimateZone.H1a,
      temperature: 15.5,
      precipitation: 850,
      humidity: 65
    }

    mount(ClimateContextDataMetrics, {
      global: {
        plugins: [pinia]
      },
      props: {
        data: mockData
      }
    })

    cy.getBySel("climate-metrics").should("exist")
  })

  it("displays temperature metric", () => {
    const pinia = createPinia()
    const mockData = {
      zone: ClimateZone.H1b,
      temperature: 18.2,
      precipitation: 900,
      humidity: 70
    }

    mount(ClimateContextDataMetrics, {
      global: {
        plugins: [pinia]
      },
      props: {
        data: mockData
      }
    })

    cy.contains("Température").should("exist")
    cy.contains("18.2").should("exist")
  })

  it("displays precipitation metric", () => {
    const pinia = createPinia()
    const mockData = {
      zone: ClimateZone.H2a,
      temperature: 16.0,
      precipitation: 750,
      humidity: 60
    }

    mount(ClimateContextDataMetrics, {
      global: {
        plugins: [pinia]
      },
      props: {
        data: mockData
      }
    })

    cy.contains("Précipitations").should("exist")
    cy.contains("750").should("exist")
  })

  it("displays humidity metric", () => {
    const pinia = createPinia()
    const mockData = {
      zone: ClimateZone.H2b,
      temperature: 17.0,
      precipitation: 800,
      humidity: 68
    }

    mount(ClimateContextDataMetrics, {
      global: {
        plugins: [pinia]
      },
      props: {
        data: mockData
      }
    })

    cy.contains("Humidité").should("exist")
    cy.contains("68").should("exist")
  })

  it("handles different climate zones", () => {
    const pinia = createPinia()
    const mockData = {
      zone: ClimateZone.H3,
      temperature: 19.5,
      precipitation: 650,
      humidity: 55
    }

    mount(ClimateContextDataMetrics, {
      global: {
        plugins: [pinia]
      },
      props: {
        data: mockData
      }
    })

    cy.getBySel("climate-metrics").should("exist")
  })

  it("renders null data gracefully", () => {
    const pinia = createPinia()

    mount(ClimateContextDataMetrics, {
      global: {
        plugins: [pinia]
      },
      props: {
        data: null
      }
    })

    cy.getBySel("empty-message").should("exist")
  })
})
