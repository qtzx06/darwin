import { SuiClient, getFullnodeUrl } from '@mysten/sui/client';
import { Transaction } from '@mysten/sui/transactions';
import { Ed25519Keypair } from '@mysten/sui/keypairs/ed25519';

// Sui client setup
const suiClient = new SuiClient({ url: getFullnodeUrl('devnet') });

// Contract IDs
const PACKAGE_ID = '0x302f582a43a8d22bc2a030ab76e3253f79618217a7a6576ad8a91b6075a85ae8';
const REGISTRY_ID = '0x44e13769132e791fca5067ddb0d13d3f50ea1488d4c5a89453227fe7b11b15b9';

// Load keypair from environment variable
const MNEMONIC = process.env.SPONSOR_MNEMONIC;

if (!MNEMONIC) {
  console.error('ERROR: SPONSOR_MNEMONIC environment variable not set!');
}

const keypair = MNEMONIC ? Ed25519Keypair.deriveKeypair(MNEMONIC) : null;

export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    if (!keypair) {
      return res.status(500).json({ error: 'Sponsor wallet not configured' });
    }

    const { agentId } = req.body;

    // Validate agentId
    if (agentId === undefined || agentId < 0 || agentId > 3) {
      return res.status(400).json({ error: 'Invalid agentId. Must be 0-3.' });
    }

    console.log(`Sponsoring vote for agent ${agentId}...`);

    // Create transaction
    const tx = new Transaction();

    tx.moveCall({
      target: `${PACKAGE_ID}::agent_votes::vote`,
      arguments: [
        tx.object(REGISTRY_ID),
        tx.pure.u8(agentId)
      ]
    });

    // Sign and execute transaction (we pay the gas)
    const result = await suiClient.signAndExecuteTransaction({
      signer: keypair,
      transaction: tx,
      options: {
        showEffects: true,
      }
    });

    console.log('Vote transaction successful:', result.digest);

    res.json({
      success: true,
      digest: result.digest,
      explorer: `https://devnet.suivision.xyz/txblock/${result.digest}`
    });

  } catch (error) {
    console.error('Vote failed:', error);
    res.status(500).json({
      error: 'Failed to submit vote',
      details: error.message
    });
  }
}
