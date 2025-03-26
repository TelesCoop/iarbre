declare namespace Cypress {
  interface Chainable<Subject = any> {
    mapClosePopup(): void
    getBySel(selector: string, ...args: any[]): Chainable
    mapHasNoPopup(): void
    mapOpenPopup(): void
    mapSwitchLayer(datatype: string): void
  }
}
