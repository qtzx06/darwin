import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSignAndExecuteTransaction, useSuiClient } from '@mysten/dapp-kit';
import { buildPlaceAndSettleTx, parseBetEvents, suiToMist, mistToSui } from '../sui/transactions';
import { BET_CHOICES, DEFAULT_BET_AMOUNTS } from '../sui/config';
import './BettingPanel.css';

export default function BettingPanel({ currentAccount }) {
  const [selectedAmount, setSelectedAmount] = useState(DEFAULT_BET_AMOUNTS[0]);
  const [customAmount, setCustomAmount] = useState('');
  const [isBetting, setIsBetting] = useState(false);
  const [lastResult, setLastResult] = useState(null);

  const { mutate: signAndExecute } = useSignAndExecuteTransaction();
  const client = useSuiClient();

  const handleBet = async (choice) => {
    if (!currentAccount) {
      alert('Please connect your wallet first');
      return;
    }

    setIsBetting(true);
    setLastResult(null);

    try {
      const betAmount = customAmount ? parseFloat(customAmount) : selectedAmount;
      const amountMIST = suiToMist(betAmount);

      const tx = buildPlaceAndSettleTx(
        amountMIST,
        choice,
        currentAccount.address
      );

      signAndExecute(
        {
          transaction: tx,
          options: {
            showEffects: true,
            showEvents: true,
          },
        },
        {
          onSuccess: (result) => {
            console.log('Bet transaction successful:', result);
            const events = parseBetEvents(result);

            if (events.settled) {
              const won = events.settled.outcome === choice;
              setLastResult({
                won,
                choice,
                outcome: events.settled.outcome,
                amount: betAmount,
                payout: mistToSui(events.settled.payout),
              });
            }
            setIsBetting(false);
          },
          onError: (error) => {
            console.error('Bet transaction failed:', error);
            alert(`Transaction failed: ${error.message}`);
            setIsBetting(false);
          },
        }
      );
    } catch (error) {
      console.error('Error building transaction:', error);
      alert(`Error: ${error.message}`);
      setIsBetting(false);
    }
  };

  return (
    <motion.div
      className="betting-panel"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <div className="betting-glass">
        <h2 className="betting-title">Place Your Bet</h2>

        {/* Amount Selection */}
        <div className="amount-section">
          <label className="section-label">Bet Amount (SUI)</label>
          <div className="amount-buttons">
            {DEFAULT_BET_AMOUNTS.map((amount) => (
              <button
                key={amount}
                className={`amount-btn ${selectedAmount === amount && !customAmount ? 'active' : ''}`}
                onClick={() => {
                  setSelectedAmount(amount);
                  setCustomAmount('');
                }}
                disabled={isBetting}
              >
                {amount} SUI
              </button>
            ))}
          </div>
          <input
            type="number"
            className="custom-amount-input"
            placeholder="Custom amount..."
            value={customAmount}
            onChange={(e) => setCustomAmount(e.target.value)}
            disabled={isBetting}
            step="0.1"
            min="0.1"
          />
        </div>

        {/* Choice Buttons */}
        <div className="choice-section">
          <label className="section-label">Choose 0 or 1</label>
          <div className="choice-buttons">
            <button
              className="choice-btn choice-zero"
              onClick={() => handleBet(BET_CHOICES.ZERO)}
              disabled={isBetting || !currentAccount}
            >
              {isBetting ? '...' : '0'}
            </button>
            <button
              className="choice-btn choice-one"
              onClick={() => handleBet(BET_CHOICES.ONE)}
              disabled={isBetting || !currentAccount}
            >
              {isBetting ? '...' : '1'}
            </button>
          </div>
        </div>

        {/* Result Display */}
        <AnimatePresence>
          {lastResult && (
            <motion.div
              className={`result-display ${lastResult.won ? 'won' : 'lost'}`}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={{ duration: 0.4 }}
            >
              <div className="result-icon">{lastResult.won ? '🎉' : '😔'}</div>
              <div className="result-text">
                {lastResult.won ? 'You Won!' : 'You Lost'}
              </div>
              <div className="result-details">
                You chose {lastResult.choice}, result was {lastResult.outcome}
              </div>
              {lastResult.won && (
                <div className="result-payout">
                  Won {lastResult.payout} SUI
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {!currentAccount && (
          <div className="connect-prompt">
            Connect your wallet to start betting
          </div>
        )}
      </div>
    </motion.div>
  );
}
