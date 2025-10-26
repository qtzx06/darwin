import { useState } from 'react';
import { useSignAndExecuteTransaction, useSuiClient } from '@mysten/dapp-kit';
import {
  buildCreateEscrowTx,
  buildAcceptEscrowTx,
  buildCancelEscrowTx,
  buildRaiseDisputeTx,
  buildResolveDisputeTx,
  parseEscrowEvents,
  extractEscrowObjectId,
} from '../sui/escrow';
import { suiToMist } from '../sui/transactions';

/**
 * Hook for escrow operations
 */
export function useEscrow() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastResult, setLastResult] = useState(null);
  
  const { mutateAsync: signAndExecute } = useSignAndExecuteTransaction();
  const client = useSuiClient();

  /**
   * Create a new escrow
   */
  const createEscrow = async (amountSUI, recipientAddress, currentAddress, options = {}) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const amountMIST = suiToMist(amountSUI);
      const tx = buildCreateEscrowTx(
        amountMIST,
        recipientAddress,
        options.arbiterAddress || null,
        options.unlockTimeMs || null,
        options.description || 'Escrow payment'
      );
      
      const result = await signAndExecute({
        transaction: tx,
        options: {
          showEffects: true,
          showObjectChanges: true,
          showEvents: true,
        },
      });
      
      // Check status
      if (result.effects?.status?.status === 'failure') {
        throw new Error(result.effects.status.error || 'Transaction failed');
      }
      
      // Extract escrow object ID
      const escrowId = extractEscrowObjectId(result.objectChanges);
      const events = parseEscrowEvents(result);
      
      const resultData = {
        digest: result.digest,
        escrowId,
        events,
        success: true,
      };
      
      setLastResult(resultData);
      return resultData;
    } catch (err) {
      const errorMsg = err.message || 'Failed to create escrow';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Accept an escrow (recipient)
   */
  const acceptEscrow = async (escrowObjectId, recipientAddress) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Wait a bit for object propagation
      await new Promise(r => setTimeout(r, 2000));
      
      const tx = buildAcceptEscrowTx(escrowObjectId, recipientAddress);
      
      const result = await signAndExecute({
        transaction: tx,
        options: {
          showEffects: true,
          showEvents: true,
        },
      });
      
      if (result.effects?.status?.status === 'failure') {
        throw new Error(result.effects.status.error || 'Transaction failed');
      }
      
      const events = parseEscrowEvents(result);
      
      const resultData = {
        digest: result.digest,
        events,
        success: true,
      };
      
      setLastResult(resultData);
      return resultData;
    } catch (err) {
      const errorMsg = err.message || 'Failed to accept escrow';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Cancel an escrow (sender)
   */
  const cancelEscrow = async (escrowObjectId, senderAddress) => {
    setIsLoading(true);
    setError(null);
    
    try {
      await new Promise(r => setTimeout(r, 2000));
      
      const tx = buildCancelEscrowTx(escrowObjectId, senderAddress);
      
      const result = await signAndExecute({
        transaction: tx,
        options: {
          showEffects: true,
          showEvents: true,
        },
      });
      
      if (result.effects?.status?.status === 'failure') {
        throw new Error(result.effects.status.error || 'Transaction failed');
      }
      
      const events = parseEscrowEvents(result);
      
      const resultData = {
        digest: result.digest,
        events,
        success: true,
      };
      
      setLastResult(resultData);
      return resultData;
    } catch (err) {
      const errorMsg = err.message || 'Failed to cancel escrow';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Raise a dispute
   */
  const raiseDispute = async (escrowObjectId) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const tx = buildRaiseDisputeTx(escrowObjectId);
      
      const result = await signAndExecute({
        transaction: tx,
        options: {
          showEffects: true,
          showEvents: true,
        },
      });
      
      if (result.effects?.status?.status === 'failure') {
        throw new Error(result.effects.status.error || 'Transaction failed');
      }
      
      const events = parseEscrowEvents(result);
      
      const resultData = {
        digest: result.digest,
        events,
        success: true,
      };
      
      setLastResult(resultData);
      return resultData;
    } catch (err) {
      const errorMsg = err.message || 'Failed to raise dispute';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Resolve a dispute (arbiter only)
   */
  const resolveDispute = async (escrowObjectId, awardToSender, winnerAddress) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const tx = buildResolveDisputeTx(escrowObjectId, awardToSender, winnerAddress);
      
      const result = await signAndExecute({
        transaction: tx,
        options: {
          showEffects: true,
          showEvents: true,
        },
      });
      
      if (result.effects?.status?.status === 'failure') {
        throw new Error(result.effects.status.error || 'Transaction failed');
      }
      
      const events = parseEscrowEvents(result);
      
      const resultData = {
        digest: result.digest,
        events,
        success: true,
      };
      
      setLastResult(resultData);
      return resultData;
    } catch (err) {
      const errorMsg = err.message || 'Failed to resolve dispute';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  return {
    createEscrow,
    acceptEscrow,
    cancelEscrow,
    raiseDispute,
    resolveDispute,
    isLoading,
    error,
    lastResult,
  };
}
