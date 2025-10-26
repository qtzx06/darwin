import { useState } from 'react';
import { useSignAndExecuteTransaction, useCurrentAccount } from '@mysten/dapp-kit';
import { Transaction } from '@mysten/sui/transactions';
import './TipModal.css';

const TIP_AMOUNTS = [0.01, 0.1, 0.5, 1.0, 5.0];

export default function TipModal({ agentName, agentWalletAddress, onClose }) {
  const [selectedAmount, setSelectedAmount] = useState(0.1);
  const [customAmount, setCustomAmount] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [txStatus, setTxStatus] = useState(null);
  
  const currentAccount = useCurrentAccount();
  const { mutate: signAndExecute } = useSignAndExecuteTransaction();

  const handleTip = async () => {
    if (!currentAccount) {
      setTxStatus({ type: 'error', message: 'Please connect your wallet first' });
      return;
    }

    const amount = customAmount ? parseFloat(customAmount) : selectedAmount;
    if (isNaN(amount) || amount <= 0) {
      setTxStatus({ type: 'error', message: 'Invalid amount' });
      return;
    }

    setIsProcessing(true);
    setTxStatus({ type: 'pending', message: 'Sending tip...' });

    try {
      const tx = new Transaction();
      
      // Convert SUI to MIST (1 SUI = 1,000,000,000 MIST)
      const amountInMist = Math.floor(amount * 1_000_000_000);
      
      // Split coins from gas and transfer to agent
      const [coin] = tx.splitCoins(tx.gas, [amountInMist]);
      tx.transferObjects([coin], agentWalletAddress);

      signAndExecute(
        {
          transaction: tx,
        },
        {
          onSuccess: (result) => {
            console.log('Tip sent successfully:', result);
            setTxStatus({
              type: 'success',
              message: `Successfully tipped ${amount} SUI to ${agentName}!`,
              digest: result.digest
            });
            setTimeout(() => onClose(), 3000);
          },
          onError: (error) => {
            console.error('Tip failed:', error);
            setTxStatus({
              type: 'error',
              message: error.message || 'Transaction failed'
            });
            setIsProcessing(false);
          },
        }
      );
    } catch (error) {
      console.error('Error building transaction:', error);
      setTxStatus({
        type: 'error',
        message: error.message || 'Failed to build transaction'
      });
      setIsProcessing(false);
    }
  };

  return (
    <div className="tip-modal-overlay" onClick={onClose}>
      <div className="tip-modal" onClick={(e) => e.stopPropagation()}>
        <button className="tip-modal-close" onClick={onClose}>×</button>
        
        <h2 className="tip-modal-title">Tip {agentName}</h2>
        <p className="tip-modal-subtitle">Show your appreciation with SUI</p>

        <div className="tip-amounts">
          {TIP_AMOUNTS.map((amount) => (
            <button
              key={amount}
              className={`tip-amount-btn ${selectedAmount === amount && !customAmount ? 'selected' : ''}`}
              onClick={() => {
                setSelectedAmount(amount);
                setCustomAmount('');
              }}
              disabled={isProcessing}
            >
              {amount} SUI
            </button>
          ))}
        </div>

        <div className="tip-custom">
          <label>Or enter custom amount:</label>
          <input
            type="number"
            step="0.01"
            min="0.01"
            placeholder="0.00"
            value={customAmount}
            onChange={(e) => setCustomAmount(e.target.value)}
            disabled={isProcessing}
            className="tip-custom-input"
          />
          <span className="tip-custom-unit">SUI</span>
        </div>

        <div className="tip-wallet-info">
          <span className="tip-wallet-label">To:</span>
          <code className="tip-wallet-address">
            {agentWalletAddress.slice(0, 8)}...{agentWalletAddress.slice(-6)}
          </code>
        </div>

        {txStatus && (
          <div className={`tip-status tip-status-${txStatus.type}`}>
            {txStatus.message}
            {txStatus.digest && (
              <a
                href={`https://testnet.suivision.xyz/txblock/${txStatus.digest}`}
                target="_blank"
                rel="noopener noreferrer"
                className="tip-tx-link"
              >
                View Transaction →
              </a>
            )}
          </div>
        )}

        <div className="tip-actions">
          <button
            className="tip-cancel-btn"
            onClick={onClose}
            disabled={isProcessing}
          >
            Cancel
          </button>
          <button
            className="tip-send-btn"
            onClick={handleTip}
            disabled={isProcessing || !currentAccount}
          >
            {isProcessing ? 'Sending...' : `Send ${customAmount || selectedAmount} SUI`}
          </button>
        </div>

        {!currentAccount && (
          <p className="tip-connect-warning">
            ⚠️ Connect your wallet to send tips
          </p>
        )}
      </div>
    </div>
  );
}
