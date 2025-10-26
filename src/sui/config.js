// SUI Network Configuration
// After deploying your Move package, update these values

export const SUI_CONFIG = {
  // Replace with your deployed package ID after running `sui client publish`
  PACKAGE_ID: import.meta.env.VITE_SUI_PACKAGE_ID || '0x0',

  // Replace with your shared House object ID after calling init_house
  HOUSE_ID: import.meta.env.VITE_SUI_HOUSE_ID || '0x0',

  // Network to use (devnet, testnet, mainnet)
  NETWORK: import.meta.env.VITE_SUI_NETWORK || 'devnet',

  // Conversion constant
  MIST_PER_SUI: 1_000_000_000,
};

// Game choices
export const BET_CHOICES = {
  ZERO: 0,
  ONE: 1,
};

// Default bet amounts in SUI
export const DEFAULT_BET_AMOUNTS = [0.1, 0.5, 1.0, 5.0];
