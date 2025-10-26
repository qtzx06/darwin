#!/usr/bin/env ts-node
import { SuiClient, getFullnodeUrl } from '@mysten/sui/client';
import { Transaction } from '@mysten/sui/transactions';
import * as dotenv from 'dotenv';
import { TestUtils, getClient, CLOCK_OBJECT_ID } from './test-utils';
import { Ed25519Keypair } from '@mysten/sui/keypairs/ed25519';

dotenv.config();

async function ensureFunds(client: SuiClient, addr: string, gasBudget: bigint) {
  const bal = await TestUtils.getBalance(client, addr);
  console.log(`Balance for ${addr.slice(0, 10)}...: ${TestUtils.formatSui(bal)} SUI`);
  if (bal < gasBudget * 10n) {
    console.log(`⚠️  Low balance, attempting faucet...`);
    try {
      await TestUtils.faucet(addr, 'testnet');
      await new Promise(r => setTimeout(r, 4000));
    } catch (e: any) {
      console.log(`⚠️  Faucet failed (${e.message}), continuing with current balance`);
    }
  }
}

async function main() {
  const client = getClient();
  const packageId = process.env.PACKAGE_ID || '';
  const gasBudget = BigInt(process.env.GAS_BUDGET || '50000000');
  if (!packageId) throw new Error('PACKAGE_ID missing in .env');

  // Keys
  const aliceKp = TestUtils.createKeypairFromEnv('ALICE_PRIVATE_KEY');
  const bobKp = TestUtils.createKeypairFromEnv('BOB_PRIVATE_KEY');
  const alice = aliceKp.getPublicKey().toSuiAddress();
  const bob = bobKp.getPublicKey().toSuiAddress();

  console.log(`📦 Package: ${packageId}`);
  console.log(`👩 Alice: ${alice}`);
  console.log(`👨 Bob:   ${bob}`);

  await ensureFunds(client, alice, gasBudget);
  await ensureFunds(client, bob, gasBudget);

  // 1) Alice create_shared escrow for Bob with SUI coin
  const tx1 = new Transaction();
  tx1.setGasBudget(Number(gasBudget));
  const [escrowCoin] = tx1.splitCoins(tx1.gas, [1_000_000n]);
  // create_shared<T>(coin, recipient, arbiter: option<address>, unlock: option<u64>, description: vector<u8>)
  tx1.moveCall({
    target: `${packageId}::escrow::create_shared`,
    typeArguments: ['0x2::sui::SUI'],
    arguments: [
      escrowCoin,
      tx1.pure.address(bob),
      // None for arbiter and unlock_time
      tx1.pure.option('address', null),
      tx1.pure.option('u64', null),
      tx1.pure.vector('u8', Array.from(new TextEncoder().encode('e2e'))),
    ],
  });

  const res1 = await client.signAndExecuteTransaction({ signer: aliceKp, transaction: tx1, options: { showEffects: true, showObjectChanges: true, showEvents: true } });
  console.log(`Transaction digest: ${res1.digest}`);
  if (res1.effects?.status?.status === 'failure') {
    console.error('Transaction failed:', res1.effects.status.error);
    throw new Error(`Transaction failed: ${res1.effects.status.error}`);
  }
  console.log(`✅ Transaction succeeded`);

  // Find created shared escrow object id
  const escrowObjectId = TestUtils.extractCreatedSharedObjectId(res1.objectChanges || []);
  if (!escrowObjectId) throw new Error('Failed to locate shared EscrowObject id');
  console.log(`✅ Escrow created: ${escrowObjectId}`);

  // Wait for object to propagate to RPC nodes
  console.log('⏳ Waiting for object propagation...');
  await new Promise(r => setTimeout(r, 3000));

  // 2) Bob accepts the escrow
  const tx2 = new Transaction();
  tx2.setGasBudget(Number(gasBudget));
  const [releasedCoin] = tx2.moveCall({
    target: `${packageId}::escrow::accept`,
    typeArguments: ['0x2::sui::SUI'],
    arguments: [
      tx2.object(escrowObjectId),
      tx2.object(CLOCK_OBJECT_ID),
    ],
  });
  // Transfer the released coin to Bob
  tx2.transferObjects([releasedCoin], bob);
  const res2 = await client.signAndExecuteTransaction({ signer: bobKp, transaction: tx2, options: { showEffects: true } });
  console.log(`Transaction digest: ${res2.digest}`);
  if (res2.effects?.status?.status === 'failure') {
    console.error('Transaction failed:', res2.effects.status.error);
    throw new Error(`Transaction failed: ${res2.effects.status.error}`);
  }
  console.log('✅ Escrow accepted by Bob');
}

main().catch((e) => { console.error(e); process.exit(1); });
