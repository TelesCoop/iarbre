/// <reference types="cypress" />
import MapPanoramaxViewer from "@/components/map/MapPanoramaxViewer.vue"
import { useMapStore } from "@/stores/map"

const picture = {
  id: "9d278906-9012-4624-875b-03df1df2c622",
  lon: 4.853768,
  lat: 45.757793,
  heading: 356,
  hasCompass: true,
  hfov: 360,
  type: "equirectangular" as const,
  sequenceId: "c3f6516d-7440-4e5b-9159-93733ce16bf6",
  nextId: null,
  prevId: null,
  assets: {
    sd: "https://panoramax.ign.fr/api/pictures/9d278906-9012-4624-875b-03df1df2c622/sd.jpg"
  },
  producer: "grand-lyon",
  license: "etalab-2.0",
  datetime: "2024-03-12T07:59:25+00:00"
}

const selectPicture = () => {
  cy.mount(MapPanoramaxViewer)
  cy.window().then(() => {
    useMapStore().selectedPanoramaxPicture = picture
  })
}

describe("MapPanoramaxViewer", () => {
  it("shows the panorama and credits the picture source", () => {
    selectPicture()

    cy.getBySel("panoramax-canvas").should("exist")
    cy.getBySel("panoramax-viewer")
      .should("contain.text", "12 mars 2024")
      .and("contain.text", "grand-lyon")
      .and("contain.text", "etalab-2.0")
    cy.getBySel("panoramax-picture-link").should(
      "have.attr",
      "href",
      `https://panoramax.ign.fr/#focus=pic&pic=${picture.id}`
    )
  })

  it("clears the selection when closed", () => {
    selectPicture()
    cy.getBySel("panoramax-viewer").should("be.visible")

    cy.getBySel("panoramax-viewer-close").click()
    cy.getBySel("panoramax-viewer").should("not.exist")
  })
})
