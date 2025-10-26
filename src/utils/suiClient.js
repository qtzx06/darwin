import { SuiClient, getFullnodeUrl } from '@mysten/sui/client';
import { Transaction } from '@mysten/sui/transactions';

// Connect to Sui devnet
export const suiClient = new SuiClient({ url: getFullnodeUrl('devnet') });

// Deployed contract IDs
export const PACKAGE_ID = '0xcf1f3a68ade5af6ecd417e8f71cc3d11ca19cfa7d5d07244962161a83f21118e';
export const REGISTRY_ID = '0x28ab822cc91b6daf3c6e6f9ba087713ec956b9369d4222f13d196f6532f82a4b';

/**
 * Vote for an agent on-chain (sponsored by backend)
 * @param {number} agentId - 0=speedrunner, 1=bloom, 2=solver, 3=loader
 */
export async function voteForAgent(agentId) {
  try {
    const response = await fetch('http://localhost:3001/api/vote', {
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
