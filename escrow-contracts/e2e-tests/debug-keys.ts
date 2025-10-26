import { Ed25519Keypair } from '@mysten/sui/keypairs/ed25519';

const kp = new Ed25519Keypair();
const secret: any = kp.getSecretKey();
console.log('Type:', typeof secret);
console.log('Length:', secret.length);
console.log('Is Uint8Array:', secret instanceof Uint8Array);
console.log('First 10 bytes:', Array.from(secret.slice(0, 10)));
