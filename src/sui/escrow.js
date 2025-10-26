import { Transaction } from '@mysten/sui/transactions';
import { SUI_CONFIG } from './config';

/**
 * Create a shared escrow for SUI coins
 * @param {bigint} amountMIST - Amount to escrow in MIST
 * @param {string} recipientAddress - Recipient's Sui address
 * @param {string|null} arbiterAddress - Optional arbiter address
 * @param {number|null} unlockTimeMs - Optional unlock timestamp in milliseconds
 * @param {string} description - Description/memo for the escrow
 * @returns {Transaction}
 */
export function buildCreateEscrowTx(amountMIST, recipientAddress, arbiterAddress = null, unlockTimeMs = null, description = '') {
  const tx = new Transaction();
  
  // Split coin for escrow
  const [escrowCoin] = tx.splitCoins(tx.gas, [amountMIST]);
  
  // Convert description to bytes
  const descBytes = Array.from(new TextEncoder().encode(description));
  
  // Build arguments
  const args = [
    escrowCoin,
    tx.pure.address(recipientAddress),
    tx.pure.option('address', arbiterAddress),
    tx.pure.option('u64', unlockTimeMs),
    tx.pure.vector('u8', descBytes),
  ];
  
  // Call create_shared
  tx.moveCall({
    target: `${SUI_CONFIG.ESCROW_PACKAGE_ID}::escrow::create_shared`,
    typeArguments: ['0x2::sui::SUI'],
    arguments: args,
  });
  
  return tx;
}

/**
 * Accept an escrow (recipient claims funds)
 * @param {string} escrowObjectId - The shared escrow object ID
 * @param {string} recipientAddress - Recipient address (for transfer)
 * @returns {Transaction}
 */
export function buildAcceptEscrowTx(escrowObjectId, recipientAddress) {
  const tx = new Transaction();
  
  // Call accept and capture returned coin
  const [releasedCoin] = tx.moveCall({
    target: `${SUI_CONFIG.ESCROW_PACKAGE_ID}::escrow::accept`,
    typeArguments: ['0x2::sui::SUI'],
    arguments: [
      tx.object(escrowObjectId),
      tx.object(SUI_CONFIG.CLOCK_ID),
    ],
  });
  
  // Transfer released coin to recipient
  tx.transferObjects([releasedCoin], recipientAddress);
  
  return tx;
}

/**
 * Cancel an escrow (sender reclaims funds)
 * @param {string} escrowObjectId - The shared escrow object ID
 * @param {string} senderAddress - Sender address (for transfer)
 * @returns {Transaction}
 */
export function buildCancelEscrowTx(escrowObjectId, senderAddress) {
  const tx = new Transaction();
  
  // Call cancel and capture returned coin
  const [returnedCoin] = tx.moveCall({
    target: `${SUI_CONFIG.ESCROW_PACKAGE_ID}::escrow::cancel`,
    typeArguments: ['0x2::sui::SUI'],
    arguments: [
      tx.object(escrowObjectId),
    ],
  });
  
  // Transfer returned coin to sender
  tx.transferObjects([returnedCoin], senderAddress);
  
  return tx;
}

/**
 * Raise a dispute on an escrow
 * @param {string} escrowObjectId - The shared escrow object ID
 * @returns {Transaction}
 */
export function buildRaiseDisputeTx(escrowObjectId) {
  const tx = new Transaction();
  
  tx.moveCall({
    target: `${SUI_CONFIG.ESCROW_PACKAGE_ID}::escrow::raise_dispute`,
    typeArguments: ['0x2::sui::SUI'],
    arguments: [
      tx.object(escrowObjectId),
    ],
  });
  
  return tx;
}

/**
 * Resolve a dispute (arbiter only)
 * @param {string} escrowObjectId - The shared escrow object ID
 * @param {boolean} awardToSender - True to award to sender, false for recipient
 * @param {string} winnerAddress - Address of the winner
 * @returns {Transaction}
 */
export function buildResolveDisputeTx(escrowObjectId, awardToSender, winnerAddress) {
  const tx = new Transaction();
  
  const [awardedCoin] = tx.moveCall({
    target: `${SUI_CONFIG.ESCROW_PACKAGE_ID}::escrow::resolve_dispute`,
    typeArguments: ['0x2::sui::SUI'],
    arguments: [
      tx.object(escrowObjectId),
      tx.pure.bool(awardToSender),
    ],
  });
  
  tx.transferObjects([awardedCoin], winnerAddress);
  
  return tx;
}

/**
 * Parse escrow events from transaction result
 * @param {object} result - Transaction result
 * @returns {object} - Parsed events
 */
export function parseEscrowEvents(result) {
  if (!result.events) return {};
  
  const created = result.events.find(e => e.type.includes('::EscrowCreated'));
  const accepted = result.events.find(e => e.type.includes('::EscrowAccepted'));
  const cancelled = result.events.find(e => e.type.includes('::EscrowCancelled'));
  const disputed = result.events.find(e => e.type.includes('::EscrowDisputed'));
  const resolved = result.events.find(e => e.type.includes('::EscrowResolved'));
  
  return {
    created: created?.parsedJson || null,
    accepted: accepted?.parsedJson || null,
    cancelled: cancelled?.parsedJson || null,
    disputed: disputed?.parsedJson || null,
    resolved: resolved?.parsedJson || null,
  };
}

/**
 * Extract created shared object ID from transaction result
 * @param {Array} objectChanges - Object changes from transaction result
 * @returns {string|null} - Escrow object ID
 */
export function extractEscrowObjectId(objectChanges) {
  if (!objectChanges) return null;
  
  for (const change of objectChanges) {
    if (change.type === 'created') {
      const isShared = change.owner && typeof change.owner === 'object' && 'Shared' in change.owner;
      if (isShared && change.objectType && change.objectType.includes('EscrowObject')) {
        return change.objectId;
      }
    }
  }
  
  return null;
}
