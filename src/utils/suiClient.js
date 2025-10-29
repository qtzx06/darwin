import { SuiClient, getFullnodeUrl } from '@mysten/sui/client';
import { Transaction } from '@mysten/sui/transactions';

// Connect to Sui devnet
export const suiClient = new SuiClient({ url: getFullnodeUrl('devnet') });

// Deployed contract IDs
export const PACKAGE_ID = '0x302f582a43a8d22bc2a030ab76e3253f79618217a7a6576ad8a91b6075a85ae8';
export const REGISTRY_ID = '0x44e13769132e791fca5067ddb0d13d3f50ea1488d4c5a89453227fe7b11b15b9';

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
