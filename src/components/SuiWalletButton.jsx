import { ConnectButton, useCurrentAccount } from '@mysten/dapp-kit';
import './SuiWalletButton.css';

export default function SuiWalletButton() {
  const currentAccount = useCurrentAccount();

  return (
    <div className="sui-wallet-button-container">
      <ConnectButton 
        connectText="Connect Wallet"
        connectedText={currentAccount ? `${currentAccount.address.slice(0, 6)}...${currentAccount.address.slice(-4)}` : 'Connected'}
      />
    </div>
  );
}
