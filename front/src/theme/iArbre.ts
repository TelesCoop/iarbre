import { definePreset } from "@primeuix/themes"
import Aura from "@primeuix/themes/aura"

const defaultPadding = {
  x: "1.5rem",
  y: "0.625rem"
}

const defaultBorder = {
  radius: "20px",
  color: "#BCBCBC"
}

const defaultPlaceholder = {
  color: "{primary.500}"
}

const defaultDropdown = {
  color: "{primary.500}"
}

const lightPrimaryColors = {
  color: "{primary.500}",
  inverseColor: "#ffffff",
  hoverColor: "{primary.600}",
  activeColor: "{primary.700}"
}

const lightSecondaryColors = {
  color: "{primary.500}",
  inverseColor: "#ffffff",
  hoverColor: "{secondary.600}",
  activeColor: "{secondary.800}"
}

export const IArbrePreset = definePreset(Aura, {
  semantic: {
    primary: {
      50: "#EDF5E9",
      100: "#C7DBC0",
      200: "#97B090",
      300: "#7A9374",
      400: "#6D8766",
      500: "#426A45",
      600: "#49673F",
      700: "#34522A",
      800: "#2B4822",
      900: "#002814"
    },
    colorScheme: {
      light: {
        primary: lightPrimaryColors,
        secondary: lightSecondaryColors
      },
      dark: {}
    }
  },
  components: {
    select: {
      // @ts-ignore
      padding: defaultPadding,
      border: defaultBorder,
      placeholder: defaultPlaceholder,
      dropdown: defaultDropdown,
      color: "{primary.500}",
      option: {
        // @ts-ignore
        focus: {
          background: "{primary.100}"
        }
      }
    },
    inputtext: {
      // @ts-ignore
      padding: defaultPadding,
      border: defaultBorder,
      placeholder: defaultPlaceholder,
      dropdown: defaultDropdown
    },
    textarea: {
      // @ts-ignore
      padding: defaultPadding,
      border: defaultBorder,
      placeholder: defaultPlaceholder
    },
    button: {
      padding: defaultPadding,
      border: { radius: "20px" },
      colorScheme: {
        light: {
          // @ts-ignore
          primary: {
            background: "white",
            color: "{primary.500}",
            hoverColor: "{primary.500}",
            hoverBackground: "{gray.100}",
            hoverBorderColor: "#BCBCBC",
            border: {
              color: "#BCBCBC"
            }
          },
          secondary: {
            background: "{primary.500}",
            hoverBackground: "{primary.700}",
            activeBackground: "{primary.800}",
            color: "white",
            hoverColor: "white",
            activeColor: "white"
          }
        }
      }
    }
  }
})
