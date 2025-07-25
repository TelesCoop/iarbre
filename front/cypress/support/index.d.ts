declare namespace Cypress {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  interface Chainable<Subject = any> {
    mapClosePopup(): void
    getBySel(selector: string, ...args: any[]): Chainable
    mapHasNoPopup(): void
    mapOpenPopup(): void
    mapSwitchLayer(datatype: string): void
    basemapSwitchLayer(maptype: string): void
    mapZoomTo(zoom: number): void
    mapCheckQPVLayer(shouldExist: boolean): void
  }
}
