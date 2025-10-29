import { SuiClient, getFullnodeUrl } from '@mysten/sui/client';
import { Ed25519Keypair } from '@mysten/sui/keypairs/ed25519';
import dotenv from 'dotenv';

dotenv.config();

const suiClient = new SuiClient({ url: getFullnodeUrl('devnet') });
const MNEMONIC = process.env.SPONSOR_MNEMONIC;

if (!MNEMONIC) {
  console.error('ERROR: SPONSOR_MNEMONIC not set in .env');
  process.exit(1);
}

const keypair = Ed25519Keypair.deriveKeypair(MNEMONIC);
const address = keypair.getPublicKey().toSuiAddress();

console.log('Sponsor Wallet Address:', address);

try {
  const balance = await suiClient.getBalance({ owner: address });
  console.log('Balance:', Number(balance.totalBalance) / 1_000_000_000, 'SUI');

  if (Number(balance.totalBalance) === 0) {
    console.log('\n⚠️  WARNING: Sponsor wallet has 0 balance!');
    console.log('Fund it here: https://faucet.sui.io/');
  }
} catch (error) {
  console.error('Error checking balance:', error.message);
}
