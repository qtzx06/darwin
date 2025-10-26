import { Ed25519Keypair } from '@mysten/sui/keypairs/ed25519';
import { decodeSuiPrivateKey } from '@mysten/sui/cryptography';

function toHex(u8: Uint8Array): string {
  return '0x' + Buffer.from(u8).toString('hex');
}

function gen(label: string) {
  const kp = new Ed25519Keypair();
  const bech32Key = kp.getSecretKey();
  
  // Decode the bech32 key to get raw bytes
  const { secretKey } = decodeSuiPrivateKey(bech32Key);
  
  const privHex = toHex(secretKey);
  const addr = kp.getPublicKey().toSuiAddress();
  console.log(`${label}_PRIVATE_KEY=${privHex}`);
  console.log(`${label}_ADDRESS=${addr}`);
}

console.log('Add the following to your .env file:');
gen('ALICE');
gen('BOB');
