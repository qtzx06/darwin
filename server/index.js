import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { SuiClient, getFullnodeUrl } from '@mysten/sui/client';
import { Transaction } from '@mysten/sui/transactions';
import { Ed25519Keypair } from '@mysten/sui/keypairs/ed25519';
import { decodeSuiPrivateKey } from '@mysten/sui/cryptography';
import { AccessToken } from 'livekit-server-sdk';

// Load environment variables
dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

// Sui client setup
const suiClient = new SuiClient({ url: getFullnodeUrl('devnet') });

// Contract IDs (Updated after deployment)
const PACKAGE_ID = '0xe649e16e62ffeaa9fdf8e2132e29c5704ac70292e0c73e4faf01313d66270c55';
const REGISTRY_ID = '0xf87ad1c43397ce66942ff74b15d367c57842d6aaf1dbea4e1a195f0eead405c3';

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

// LiveKit token generation endpoint
app.post('/api/livekit/token', (req, res) => {
  try {
    const { roomName, participantName } = req.body;

    if (!roomName || !participantName) {
      return res.status(400).json({ error: 'roomName and participantName are required' });
    }

    const apiKey = process.env.VITE_LIVEKIT_API_KEY;
    const apiSecret = process.env.VITE_LIVEKIT_API_SECRET;

    if (!apiKey || !apiSecret) {
      return res.status(500).json({ error: 'LiveKit credentials not configured' });
    }

    // Create access token
    const at = new AccessToken(apiKey, apiSecret, {
      identity: participantName,
      ttl: '1h',
    });

    at.addGrant({
      room: roomName,
      roomJoin: true,
      canPublish: true,
      canSubscribe: true,
      canPublishData: true,
    });

    const token = await at.toJwt();

    console.log(`Generated LiveKit token for ${participantName} in room ${roomName}`);
    console.log(`Token type: ${typeof token}, Token preview: ${token.substring(0, 50)}...`);

    res.json({ token });
  } catch (error) {
    console.error('Failed to generate LiveKit token:', error);
    res.status(500).json({ error: 'Failed to generate token', details: error.message });
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
