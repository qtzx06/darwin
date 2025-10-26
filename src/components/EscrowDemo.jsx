import { useState } from 'react';
import { useCurrentAccount } from '@mysten/dapp-kit';
import { useEscrow } from '../hooks/useEscrow';
import './EscrowDemo.css';

export default function EscrowDemo() {
  const currentAccount = useCurrentAccount();
  const { createEscrow, acceptEscrow, cancelEscrow, isLoading, error, lastResult } = useEscrow();
  
  const [amount, setAmount] = useState('0.01');
  const [recipient, setRecipient] = useState('');
  const [description, setDescription] = useState('');
  const [activeEscrowId, setActiveEscrowId] = useState('');

  const handleCreateEscrow = async () => {
    if (!currentAccount?.address) {
      alert('Please connect your wallet');
      return;
    }
    
    if (!recipient || !amount) {
      alert('Please fill in all fields');
      return;
    }
    
    try {
      const result = await createEscrow(
        parseFloat(amount),
        recipient,
        currentAccount.address,
        { description: description || 'Payment via Darwin' }
      );
      
      if (result.escrowId) {
        setActiveEscrowId(result.escrowId);
        alert(`Escrow created! ID: ${result.escrowId}`);
      }
    } catch (err) {
      console.error('Create escrow error:', err);
      alert(`Error: ${err.message}`);
    }
  };

  const handleAcceptEscrow = async () => {
    if (!currentAccount?.address) {
      alert('Please connect your wallet');
      return;
    }
    
    if (!activeEscrowId) {
      alert('Please enter an escrow ID');
      return;
    }
    
    try {
      await acceptEscrow(activeEscrowId, currentAccount.address);
      alert('Escrow accepted successfully!');
      setActiveEscrowId('');
    } catch (err) {
      console.error('Accept escrow error:', err);
      alert(`Error: ${err.message}`);
    }
  };

  const handleCancelEscrow = async () => {
    if (!currentAccount?.address) {
      alert('Please connect your wallet');
      return;
    }
    
    if (!activeEscrowId) {
      alert('Please enter an escrow ID');
      return;
    }
    
    try {
      await cancelEscrow(activeEscrowId, currentAccount.address);
      alert('Escrow cancelled successfully!');
      setActiveEscrowId('');
    } catch (err) {
      console.error('Cancel escrow error:', err);
      alert(`Error: ${err.message}`);
    }
  };

  return (
    <div className="escrow-demo">
      <h2>Escrow Demo</h2>
      
      {!currentAccount && (
        <div className="warning">Please connect your Sui wallet to use escrow</div>
      )}
      
      <div className="escrow-section">
        <h3>Create Escrow</h3>
        <div className="form-group">
          <label>Amount (SUI):</label>
          <input
            type="number"
            step="0.01"
            min="0.01"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="0.01"
          />
        </div>
        
        <div className="form-group">
          <label>Recipient Address:</label>
          <input
            type="text"
            value={recipient}
            onChange={(e) => setRecipient(e.target.value)}
            placeholder="0x..."
          />
        </div>
        
        <div className="form-group">
          <label>Description (optional):</label>
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Payment for services"
          />
        </div>
        
        <button
          onClick={handleCreateEscrow}
          disabled={isLoading || !currentAccount}
          className="btn-primary"
        >
          {isLoading ? 'Creating...' : 'Create Escrow'}
        </button>
      </div>
      
      <div className="escrow-section">
        <h3>Manage Escrow</h3>
        <div className="form-group">
          <label>Escrow Object ID:</label>
          <input
            type="text"
            value={activeEscrowId}
            onChange={(e) => setActiveEscrowId(e.target.value)}
            placeholder="0x..."
          />
        </div>
        
        <div className="button-group">
          <button
            onClick={handleAcceptEscrow}
            disabled={isLoading || !currentAccount || !activeEscrowId}
            className="btn-success"
          >
            {isLoading ? 'Processing...' : 'Accept (Recipient)'}
          </button>
          
          <button
            onClick={handleCancelEscrow}
            disabled={isLoading || !currentAccount || !activeEscrowId}
            className="btn-danger"
          >
            {isLoading ? 'Processing...' : 'Cancel (Sender)'}
          </button>
        </div>
      </div>
      
      {error && (
        <div className="error-message">
          Error: {error}
        </div>
      )}
      
      {lastResult && (
        <div className="result-message">
          <h4>Last Transaction:</h4>
          <p>Digest: <code>{lastResult.digest}</code></p>
          {lastResult.escrowId && (
            <p>Escrow ID: <code>{lastResult.escrowId}</code></p>
          )}
        </div>
      )}
    </div>
  );
}
