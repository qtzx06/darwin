import express from 'express';
import cors from 'cors';
import { SuiClient, getFullnodeUrl } from '@mysten/sui/client';
import { Transaction } from '@mysten/sui/transactions';
import { Ed25519Keypair } from '@mysten/sui/keypairs/ed25519';
import { decodeSuiPrivateKey } from '@mysten/sui/cryptography';

const app = express();
app.use(cors());
app.use(express.json());

// Sui client setup
const suiClient = new SuiClient({ url: getFullnodeUrl('devnet') });

// Contract IDs
const PACKAGE_ID = '0xcf1f3a68ade5af6ecd417e8f71cc3d11ca19cfa7d5d07244962161a83f21118e';
const REGISTRY_ID = '0x28ab822cc91b6daf3c6e6f9ba087713ec956b9369d4222f13d196f6532f82a4b';

// Load keypair from mnemonic (stored in .env file)
const MNEMONIC = process.env.SPONSOR_MNEMONIC;

if (!MNEMONIC) {
  console.error('ERROR: SPONSOR_MNEMONIC environment variable not set!');
  console.error('Please create a .env file with your mnemonic');
  process.exit(1);
}

// Derive keypair from mnemonic
const keypair = Ed25519Keypair.deriveKeypair(MNEMONIC);

console.log('Sponsor address:', keypair.getPublicKey().toSuiAddress());

// API endpoint to sponsor a vote
app.post('/api/vote', async (req, res) => {
  try {
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
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', sponsor: keypair.getPublicKey().toSuiAddress() });
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`Sponsor server running on http://localhost:${PORT}`);
  console.log(`Sponsor address: ${keypair.getPublicKey().toSuiAddress()}`);
});
