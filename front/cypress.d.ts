import { mount } from "cypress/vue"
import { VueElementConstructor } from "vue"

declare global {
  namespace Cypress {
    interface Chainable {
      mount: typeof mount

      mount(component: VueElementConstructor, options?: MountingOptions): Chainable<Element>
    }
  }
}
