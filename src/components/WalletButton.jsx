import { useCurrentAccount, useConnectWallet, useDisconnectWallet } from '@mysten/dapp-kit';
import './WalletButton.css';

function WalletButton() {
  const currentAccount = useCurrentAccount();
  const { mutate: connect } = useConnectWallet();
  const { mutate: disconnect } = useDisconnectWallet();

  const formatAddress = (address) => {
    if (!address) return '';
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  if (currentAccount) {
    return (
      <button className="wallet-button connected" onClick={() => disconnect()}>
        <div className="wallet-status">
          <span className="wallet-indicator"></span>
          <span className="wallet-address">{formatAddress(currentAccount.address)}</span>
        </div>
      </button>
    );
  }

  return (
    <button className="wallet-button" onClick={() => connect({ wallet: null })}>
      <span className="wallet-icon">🔐</span>
      <span>Connect Wallet</span>
    </button>
  );
}

export default WalletButton;
