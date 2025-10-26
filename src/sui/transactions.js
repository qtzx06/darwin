import { Transaction } from '@mysten/sui/transactions';
import { SUI_CONFIG } from './config';

/**
 * Build a PTB (Programmable Transaction Block) that places a bet and immediately settles it.
 * @param {bigint} amountMIST - Amount to bet in MIST (1 SUI = 1_000_000_000 MIST)
 * @param {number} choice - User's choice (0 or 1)
 * @param {string} sender - Sender's SUI address
 * @returns {Transaction} - The transaction block to execute
 */
export function buildPlaceAndSettleTx(amountMIST, choice, sender) {
  const tx = new Transaction();

  // 1) Split SUI coin for the bet amount
  const [betCoin] = tx.splitCoins(tx.gas, [amountMIST]);

  // 2) place_bet(house, betCoin, amount, choice)
  tx.moveCall({
    target: `${SUI_CONFIG.PACKAGE_ID}::colosseum_bets::place_bet`,
    arguments: [
      tx.object(SUI_CONFIG.HOUSE_ID),
      betCoin,
      tx.pure.u64(amountMIST),
      tx.pure.u8(choice),
    ],
  });

  // 3) settle_bet(house, random, player, amount, choice)
  // Note: Random object is at a well-known address on Sui
  tx.moveCall({
    target: `${SUI_CONFIG.PACKAGE_ID}::colosseum_bets::settle_bet`,
    arguments: [
      tx.object(SUI_CONFIG.HOUSE_ID),
      tx.object('0x8'), // Random object address on Sui
      tx.pure.address(sender),
      tx.pure.u64(amountMIST),
      tx.pure.u8(choice),
    ],
  });

  return tx;
}

/**
 * Build a transaction to deposit SUI into the house pot.
 * @param {bigint} amountMIST - Amount to deposit in MIST
 * @returns {Transaction}
 */
export function buildDepositTx(amountMIST) {
  const tx = new Transaction();

  const [depositCoin] = tx.splitCoins(tx.gas, [amountMIST]);

  tx.moveCall({
    target: `${SUI_CONFIG.PACKAGE_ID}::colosseum_bets::deposit`,
    arguments: [
      tx.object(SUI_CONFIG.HOUSE_ID),
      depositCoin,
    ],
  });

  return tx;
}

/**
 * Parse bet events from transaction result
 * @param {object} result - Transaction result from signAndExecuteTransaction
 * @returns {object} - Parsed bet data with { placed, settled }
 */
export function parseBetEvents(result) {
  if (!result.events) return { placed: null, settled: null };

  const betPlaced = result.events.find(e =>
    e.type.includes('::BetPlaced')
  );

  const betSettled = result.events.find(e =>
    e.type.includes('::BetSettled')
  );

  return {
    placed: betPlaced ? betPlaced.parsedJson : null,
    settled: betSettled ? betSettled.parsedJson : null,
  };
}

/**
 * Convert SUI amount to MIST
 * @param {number} sui - Amount in SUI
 * @returns {bigint} - Amount in MIST
 */
export function suiToMist(sui) {
  return BigInt(Math.floor(sui * SUI_CONFIG.MIST_PER_SUI));
}

/**
 * Convert MIST amount to SUI
 * @param {bigint|string|number} mist - Amount in MIST
 * @returns {number} - Amount in SUI
 */
export function mistToSui(mist) {
  return Number(mist) / SUI_CONFIG.MIST_PER_SUI;
}
