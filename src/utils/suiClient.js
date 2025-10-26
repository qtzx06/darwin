import { SuiClient, getFullnodeUrl } from '@mysten/sui/client';
import { Transaction } from '@mysten/sui/transactions';
import agentWallets from './agentWallets.json';

// Connect to Sui devnet
export const suiClient = new SuiClient({ url: getFullnodeUrl('devnet') });

// Deployed contract IDs
export const PACKAGE_ID = '0xe649e16e62ffeaa9fdf8e2132e29c5704ac70292e0c73e4faf01313d66270c55';
export const REGISTRY_ID = '0xf87ad1c43397ce66942ff74b15d367c57842d6aaf1dbea4e1a195f0eead405c3';

// Agent wallet addresses
export const AGENT_WALLETS = agentWallets;

/**
 * Vote for an agent on-chain (sponsored by backend)
 * @param {number} agentId - 0=speedrunner, 1=bloom, 2=solver, 3=loader
 */
export async function voteForAgent(agentId) {
  try {
    const response = await fetch('/api/vote', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ agentId }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Failed to vote');
    }

    console.log('Vote transaction successful:', data);
    return data;
  } catch (error) {
    console.error('Vote transaction failed:', error);
    throw error;
  }
}

/**
 * Get all vote counts from the registry
 */
export async function getVoteCounts() {
  try {
    const object = await suiClient.getObject({
      id: REGISTRY_ID,
      options: {
        showContent: true
      }
    });

    if (object.data && object.data.content && object.data.content.fields) {
      const fields = object.data.content.fields;
      return {
        speedrunner: parseInt(fields.speedrunner_votes),
        bloom: parseInt(fields.bloom_votes),
        solver: parseInt(fields.solver_votes),
        loader: parseInt(fields.loader_votes)
      };
    }

    return { speedrunner: 0, bloom: 0, solver: 0, loader: 0 };
  } catch (error) {
    console.error('Failed to fetch vote counts:', error);
    return { speedrunner: 0, bloom: 0, solver: 0, loader: 0 };
  }
}

/**
 * Vote for an agent with a SUI tip (user-signed transaction)
 * @param {number} agentId - 0=speedrunner, 1=bloom, 2=solver, 3=loader
 * @param {number} tipAmount - Amount in SUI to tip
 * @param {object} signAndExecuteTransaction - Wallet's sign function
 */
export async function voteWithTip(agentId, tipAmount, signAndExecuteTransaction) {
  try {
    const tx = new Transaction();
    
    // Convert SUI to MIST (1 SUI = 1,000,000,000 MIST)
    const tipAmountMist = Math.floor(tipAmount * 1_000_000_000);
    
    // Split coins from gas for the tip
    const [coin] = tx.splitCoins(tx.gas, [tx.pure.u64(tipAmountMist)]);
    
    // Call vote_with_tip function
    tx.moveCall({
      target: `${PACKAGE_ID}::agent_votes::vote_with_tip`,
      arguments: [
        tx.object(REGISTRY_ID),
        tx.pure.u8(agentId),
        coin
      ]
    });
    
    // User signs and executes the transaction
    const result = await signAndExecuteTransaction({
      transaction: tx,
      options: {
        showEffects: true,
      }
    });
    
    console.log('Vote with tip successful:', result.digest);
    return {
      success: true,
      digest: result.digest,
      explorer: `https://devnet.suivision.xyz/txblock/${result.digest}`
    };
  } catch (error) {
    console.error('Vote with tip failed:', error);
    throw error;
  }
}

/**
 * Get agent wallet address by agent name
 * @param {string} agentName - Agent name (speedrunner, bloom, solver, loader)
 */
export function getAgentWalletAddress(agentName) {
  return AGENT_WALLETS[agentName.toLowerCase()] || null;
}

/**
 * Get SUI balance for an address
 * @param {string} address - Sui address
 */
export async function getSuiBalance(address) {
  try {
    const balance = await suiClient.getBalance({
      owner: address,
      coinType: '0x2::sui::SUI'
    });
    
    // Convert from MIST to SUI
    return parseInt(balance.totalBalance) / 1_000_000_000;
  } catch (error) {
    console.error('Failed to fetch balance:', error);
    return 0;
  }
}

/**
 * Get SUI balances for all agent wallets
 */
export async function getAgentWalletBalances() {
  try {
    const balances = {};
    
    for (const [agent, address] of Object.entries(AGENT_WALLETS)) {
      balances[agent] = await getSuiBalance(address);
    }
    
    return balances;
  } catch (error) {
    console.error('Failed to fetch agent balances:', error);
    return { speedrunner: 0, bloom: 0, solver: 0, loader: 0 };
  }
}
