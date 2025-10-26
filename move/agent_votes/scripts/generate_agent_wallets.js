#!/usr/bin/env node
/**
 * Generate 4 Sui keypairs for agent wallets
 * Run: node generate_agent_wallets.js
 */

import { Ed25519Keypair } from '@mysten/sui/keypairs/ed25519';
import { writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const agents = ['speedrunner', 'bloom', 'solver', 'loader'];
const wallets = {};
const privateKeys = {};

console.log('🔐 Generating Sui wallets for agents...\n');

for (const agent of agents) {
  const keypair = new Ed25519Keypair();
  const address = keypair.getPublicKey().toSuiAddress();
  const secretKey = keypair.getSecretKey();
  
  wallets[agent] = address;
  privateKeys[agent] = Buffer.from(secretKey).toString('hex');
  
  console.log(`${agent.toUpperCase()}:`);
  console.log(`  Address: ${address}`);
  console.log(`  Private Key: ${Buffer.from(secretKey).toString('hex')}`);
  console.log('');
}

// Save public addresses to config
const configPath = join(__dirname, '../../config/agent_wallets.json');
writeFileSync(configPath, JSON.stringify(wallets, null, 2));
console.log(`✅ Public addresses saved to: ${configPath}`);

// Save private keys to .env format (for manual copy)
const envPath = join(__dirname, '../../config/agent_wallets.env');
let envContent = '# Agent Wallet Private Keys - KEEP SECRET!\n';
envContent += '# Add these to your .env file if you want to access agent wallets\n\n';
for (const agent of agents) {
  envContent += `${agent.toUpperCase()}_WALLET_PRIVATE_KEY=${privateKeys[agent]}\n`;
}
writeFileSync(envPath, envContent);
console.log(`✅ Private keys saved to: ${envPath}`);

console.log('\n⚠️  IMPORTANT: Keep private keys secure!');
console.log('💡 Agent wallets can be receive-only (no need to use private keys)');
console.log('💡 Private keys are only needed if agents need to spend SUI');

