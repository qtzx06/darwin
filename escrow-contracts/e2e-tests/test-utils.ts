import { SuiClient, getFullnodeUrl } from '@mysten/sui/client';
import { Transaction } from '@mysten/sui/transactions';
import { Ed25519Keypair } from '@mysten/sui/keypairs/ed25519';
import { decodeSuiPrivateKey } from '@mysten/sui/cryptography';

export interface TestUser {
  name: string;
  keypair: Ed25519Keypair;
  address: string;
}

export class TestUtils {
  static createKeypairFromEnv(envVar: string): Ed25519Keypair {
    const privateKey = process.env[envVar];
    if (!privateKey) throw new Error(`${envVar} not found. Run: npm run generate-keys`);

    if (privateKey.startsWith('suiprivkey1')) {
      const { schema, secretKey } = decodeSuiPrivateKey(privateKey);
      if (schema !== 'ED25519') throw new Error(`Unsupported key schema: ${schema}`);
      return Ed25519Keypair.fromSecretKey(secretKey);
    }
    if (privateKey.startsWith('0x')) {
      let secretKey = Uint8Array.from(Buffer.from(privateKey.slice(2), 'hex'));
      // Ed25519 expects 32-byte seed; if we got 64 bytes, take first 32
      if (secretKey.length === 64) {
        secretKey = secretKey.slice(0, 32);
      }
      return Ed25519Keypair.fromSecretKey(secretKey);
    }
    throw new Error('Invalid private key format');
  }

  static async waitForSuccess(client: SuiClient, digest: string, timeoutMs = 45000): Promise<void> {
    const start = Date.now();
    while (Date.now() - start < timeoutMs) {
      try {
        const res = await client.getTransactionBlock({ digest, options: { showEffects: true } });
        const status = res.effects?.status?.status;
        if (status === 'success') return;
        if (status === 'failure') throw new Error(res.effects?.status.error || 'tx failed');
      } catch (e: any) {
        if (!String(e.message || '').includes('not found')) throw e;
      }
      await new Promise(r => setTimeout(r, 1500));
    }
    throw new Error(`Timeout waiting for ${digest}`);
  }

  static async getBalance(client: SuiClient, address: string): Promise<bigint> {
    const coins = await client.getCoins({ owner: address });
    return coins.data.reduce((sum, c) => sum + BigInt(c.balance), 0n);
  }

  static async faucet(address: string, network: 'testnet' | 'devnet' = 'testnet') {
    const url = `https://faucet.${network}.sui.io/gas`;
    const res = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ FixedAmountRequest: { recipient: address } }) });
    if (!res.ok) throw new Error(`Faucet failed: ${res.statusText}`);
  }

  static formatSui(mist: bigint) { return (Number(mist) / 1_000_000_000).toFixed(4); }

  static extractCreatedSharedObjectId(objChanges: any[], typeSubstring?: string): string | null {
    for (const oc of objChanges || []) {
      if (oc.type === 'created') {
        const isShared = oc.owner && typeof oc.owner === 'object' && 'Shared' in oc.owner;
        if (isShared && (!typeSubstring || (oc.objectType && String(oc.objectType).includes(typeSubstring)))) {
          return oc.objectId;
        }
      }
    }
    return null;
  }
}

export function getClient(): SuiClient {
  return new SuiClient({ url: process.env.SUI_RPC_URL || getFullnodeUrl('testnet') });
}

export const CLOCK_OBJECT_ID = '0x6';
