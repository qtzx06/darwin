#!/bin/bash

# Demo Atomic Swap Script
# Creates a sample swap between two parties

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════╗"
echo "║        Atomic Swap Demo Script            ║"
echo "╚═══════════════════════════════════════════╝"
echo -e "${NC}"

# Get deployment info
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CURRENT_ENV=$(sui client active-env)
DEPLOY_FILE="$SCRIPT_DIR/deployment-${CURRENT_ENV}.json"

if [ ! -f "$DEPLOY_FILE" ]; then
    echo -e "${YELLOW}⚠️  No deployment found for $CURRENT_ENV${NC}"
    echo "Please run ./scripts/deploy.sh first"
    exit 1
fi

PACKAGE_ID=$(jq -r '.packageId' "$DEPLOY_FILE")
echo -e "${GREEN}✅ Package ID: $PACKAGE_ID${NC}"
echo ""

# Get current address (Party A)
PARTY_A=$(sui client active-address)
echo -e "${BLUE}Party A (you): $PARTY_A${NC}"
echo ""

# Ask for Party B
read -p "Enter Party B address (or press Enter to use your own for testing): " PARTY_B
if [ -z "$PARTY_B" ]; then
    PARTY_B=$PARTY_A
    echo "Using your address as Party B (testing mode)"
fi

echo ""
echo -e "${BLUE}Creating atomic swap...${NC}"
echo "  Party A offers: 0.05 SUI (50000000 MIST)"
echo "  Party B offers: 0.1 SUI (100000000 MIST)"
echo "  Expiration: 1 hour from now"
echo ""

# Calculate expiration (1 hour from now in milliseconds)
EXPIRATION=$(( $(date +%s) * 1000 + 3600000 ))

# Create swap
echo "Creating swap..."
CREATE_OUTPUT=$(sui client call \
  --package "$PACKAGE_ID" \
  --module escrow \
  --function create_swap \
  --type-args "0x2::sui::SUI" "0x2::sui::SUI" \
  --args "$PARTY_B" 50000000 100000000 "$EXPIRATION" \
  --gas-budget 100000000 \
  --json)

# Extract swap ID
SWAP_ID=$(echo "$CREATE_OUTPUT" | jq -r '.objectChanges[] | select(.objectType | contains("::escrow::SwapEscrow")) | .objectId')

if [ -z "$SWAP_ID" ]; then
    echo "❌ Failed to create swap"
    exit 1
fi

echo -e "${GREEN}✅ Swap created!${NC}"
echo -e "${GREEN}Swap ID: $SWAP_ID${NC}"
echo ""

# Party A deposits
echo -e "${BLUE}Party A depositing 0.05 SUI...${NC}"

# Get a gas coin
GAS_COINS=$(sui client gas --json)
FIRST_COIN=$(echo "$GAS_COINS" | jq -r '.[0].gasCoinId')

# Split coin for swap
SPLIT_OUTPUT=$(sui client split-coin --coin-id "$FIRST_COIN" --amounts 50000000 --gas-budget 10000000 --json)
COIN_A=$(echo "$SPLIT_OUTPUT" | jq -r '.objectChanges[] | select(.objectType | contains("0x2::coin::Coin")) | .objectId' | head -1)

# Deposit
sui client call \
  --package "$PACKAGE_ID" \
  --module escrow \
  --function swap_deposit_a \
  --type-args "0x2::sui::SUI" "0x2::sui::SUI" \
  --args "$SWAP_ID" "$COIN_A" \
  --gas-budget 100000000 > /dev/null

echo -e "${GREEN}✅ Party A deposited${NC}"
echo ""

# Save swap info
cat > "$SCRIPT_DIR/demo-swap.json" << EOF
{
  "swapId": "$SWAP_ID",
  "partyA": "$PARTY_A",
  "partyB": "$PARTY_B",
  "amountA": "50000000",
  "amountB": "100000000",
  "expiration": "$EXPIRATION",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

echo -e "${GREEN}✅ Swap details saved to: scripts/demo-swap.json${NC}"
echo ""

# Show next steps
echo -e "${BLUE}╔═══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Swap Created (Partial)            ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Swap is half-complete. Party A has deposited.${NC}"
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo ""
echo "1. Party B must deposit 0.1 SUI:"
echo -e "   ${YELLOW}# Split coin first${NC}"
echo -e "   ${YELLOW}sui client split-coin --coin-id <COIN_ID> --amounts 100000000${NC}"
echo ""
echo -e "   ${YELLOW}# Then deposit${NC}"
echo -e "   ${YELLOW}sui client call \\${NC}"
echo -e "     ${YELLOW}--package $PACKAGE_ID \\${NC}"
echo -e "     ${YELLOW}--module escrow \\${NC}"
echo -e "     ${YELLOW}--function swap_deposit_b \\${NC}"
echo -e "     ${YELLOW}--type-args 0x2::sui::SUI 0x2::sui::SUI \\${NC}"
echo -e "     ${YELLOW}--args $SWAP_ID <NEW_COIN_ID> \\${NC}"
echo -e "     ${YELLOW}--gas-budget 100000000${NC}"
echo ""
echo "2. After both parties deposit, execute the swap:"
echo -e "   ${YELLOW}sui client call \\${NC}"
echo -e "     ${YELLOW}--package $PACKAGE_ID \\${NC}"
echo -e "     ${YELLOW}--module escrow \\${NC}"
echo -e "     ${YELLOW}--function execute_swap \\${NC}"
echo -e "     ${YELLOW}--type-args 0x2::sui::SUI 0x2::sui::SUI \\${NC}"
echo -e "     ${YELLOW}--args $SWAP_ID 0x6 \\${NC}"
echo -e "     ${YELLOW}--gas-budget 100000000${NC}"
echo ""

# If testing mode (same person for both parties)
if [ "$PARTY_A" == "$PARTY_B" ]; then
    echo ""
    read -p "Complete the swap now? (you are both parties) (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "Party B depositing 0.1 SUI..."

        # Split another coin
        SPLIT_OUTPUT2=$(sui client split-coin --coin-id "$FIRST_COIN" --amounts 100000000 --gas-budget 10000000 --json)
        COIN_B=$(echo "$SPLIT_OUTPUT2" | jq -r '.objectChanges[] | select(.objectType | contains("0x2::coin::Coin")) | .objectId' | head -1)

        # Deposit as Party B
        sui client call \
          --package "$PACKAGE_ID" \
          --module escrow \
          --function swap_deposit_b \
          --type-args "0x2::sui::SUI" "0x2::sui::SUI" \
          --args "$SWAP_ID" "$COIN_B" \
          --gas-budget 100000000 > /dev/null

        echo -e "${GREEN}✅ Party B deposited${NC}"
        echo ""

        # Execute swap
        echo "Executing swap..."
        sui client call \
          --package "$PACKAGE_ID" \
          --module escrow \
          --function execute_swap \
          --type-args "0x2::sui::SUI" "0x2::sui::SUI" \
          --args "$SWAP_ID" "0x6" \
          --gas-budget 100000000

        echo ""
        echo -e "${GREEN}✅ Swap executed successfully!${NC}"
        echo "Check your wallet - you should have received the swapped amount."
    fi
fi

echo ""
echo -e "${GREEN}🎉 Demo complete!${NC}"
