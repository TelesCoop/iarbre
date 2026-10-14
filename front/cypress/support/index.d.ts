declare namespace Cypress {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  interface Chainable<Subject = any> {
    getBySel(selector: string, ...args: any[]): Chainable
    visitMap(viewport: { width: number; height: number }, path?: string): void
    mapStore(): Chainable<any>
    mapSwitchLayer(datatype: string): void
    basemapSwitchLayer(maptype: string): void
    mapZoomTo(zoom: number): void
    mapCheckQPVLayer(shouldExist: boolean): void
    mapCheckCadastreLayer(shouldExist: boolean): void
    mapCheckPanoramaxLayer(shouldExist: boolean): void
  }
}
