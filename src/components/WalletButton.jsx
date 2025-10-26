import { useState } from 'react';
import { ConnectButton, useCurrentAccount } from '@mysten/dapp-kit';
import './WalletButton.css';

export default function WalletButton() {
  const currentAccount = useCurrentAccount();
  const [showAddress, setShowAddress] = useState(false);

  const formatAddress = (address) => {
    if (!address) return '';
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  return (
    <div className="wallet-button-container">
      <ConnectButton
        connectText="Connect Wallet"
        connectedText={formatAddress(currentAccount?.address)}
        className="wallet-connect-btn"
      />
      {currentAccount && (
        <button
          className="wallet-info-btn"
          onClick={() => setShowAddress(!showAddress)}
          title="Toggle address display"
        >
          ⓘ
        </button>
      )}
      {showAddress && currentAccount && (
        <div className="wallet-address-display">
          {currentAccount.address}
        </div>
      )}
    </div>
  );
}
