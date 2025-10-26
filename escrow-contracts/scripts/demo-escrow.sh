#!/bin/bash

# Demo Escrow Script
# Creates a sample escrow to demonstrate functionality

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════╗"
echo "║        Escrow Demo Script                 ║"
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

# Get current address
SENDER=$(sui client active-address)
echo -e "${BLUE}Sender: $SENDER${NC}"
echo ""

# Ask for recipient
read -p "Enter recipient address (or press Enter to use your own address): " RECIPIENT
if [ -z "$RECIPIENT" ]; then
    RECIPIENT=$SENDER
    echo "Using sender address as recipient (testing mode)"
fi

echo ""
echo -e "${BLUE}Creating demo escrow...${NC}"
echo "  Amount: 0.1 SUI (100000000 MIST)"
echo "  Recipient: $RECIPIENT"
echo "  Description: 'Demo escrow payment'"
echo ""

# Get a gas coin
GAS_COINS=$(sui client gas --json)
FIRST_COIN=$(echo "$GAS_COINS" | jq -r '.[0].gasCoinId')

if [ -z "$FIRST_COIN" ] || [ "$FIRST_COIN" == "null" ]; then
    echo "❌ No gas coins found"
    exit 1
fi

# Split coin for escrow (0.1 SUI)
echo "Splitting coin for escrow..."
SPLIT_OUTPUT=$(sui client split-coin --coin-id "$FIRST_COIN" --amounts 100000000 --gas-budget 10000000 --json)
ESCROW_COIN=$(echo "$SPLIT_OUTPUT" | jq -r '.objectChanges[] | select(.objectType | contains("0x2::coin::Coin")) | .objectId' | head -1)

if [ -z "$ESCROW_COIN" ]; then
    echo "❌ Failed to split coin"
    exit 1
fi

echo -e "${GREEN}✅ Coin split: $ESCROW_COIN${NC}"
echo ""

# Create escrow
echo "Creating escrow..."
DESCRIPTION_HEX=$(echo -n "Demo escrow payment" | xxd -p | tr -d '\n')

CREATE_OUTPUT=$(sui client call \
  --package "$PACKAGE_ID" \
  --module escrow \
  --function create_shared \
  --type-args "0x2::sui::SUI" \
  --args "$ESCROW_COIN" "$RECIPIENT" "[]" "[]" "0x$DESCRIPTION_HEX" \
  --gas-budget 100000000 \
  --json)

# Extract escrow ID
ESCROW_ID=$(echo "$CREATE_OUTPUT" | jq -r '.objectChanges[] | select(.objectType | contains("::escrow::EscrowObject")) | .objectId')

if [ -z "$ESCROW_ID" ]; then
    echo "❌ Failed to create escrow"
    echo "$CREATE_OUTPUT" | jq '.'
    exit 1
fi

echo -e "${GREEN}✅ Escrow created!${NC}"
echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Escrow Created Successfully       ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Escrow ID:${NC}  $ESCROW_ID"
echo -e "${GREEN}Amount:${NC}     0.1 SUI"
echo -e "${GREEN}Recipient:${NC}  $RECIPIENT"
echo ""

# Save escrow info
cat > "$SCRIPT_DIR/demo-escrow.json" << EOF
{
  "escrowId": "$ESCROW_ID",
  "sender": "$SENDER",
  "recipient": "$RECIPIENT",
  "amount": "100000000",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

echo -e "${GREEN}✅ Escrow details saved to: scripts/demo-escrow.json${NC}"
echo ""

# Show next steps
echo -e "${BLUE}📝 Next Steps:${NC}"
echo ""
echo "1. View escrow on explorer:"
if [ "$CURRENT_ENV" == "mainnet" ]; then
    echo -e "   ${BLUE}https://suiexplorer.com/object/$ESCROW_ID${NC}"
elif [ "$CURRENT_ENV" == "testnet" ]; then
    echo -e "   ${BLUE}https://suiexplorer.com/object/$ESCROW_ID?network=testnet${NC}"
else
    echo -e "   ${BLUE}https://suiexplorer.com/object/$ESCROW_ID?network=devnet${NC}"
fi
echo ""
echo "2. Accept the escrow (as recipient):"
echo -e "   ${YELLOW}sui client call \\${NC}"
echo -e "     ${YELLOW}--package $PACKAGE_ID \\${NC}"
echo -e "     ${YELLOW}--module escrow \\${NC}"
echo -e "     ${YELLOW}--function accept \\${NC}"
echo -e "     ${YELLOW}--type-args 0x2::sui::SUI \\${NC}"
echo -e "     ${YELLOW}--args $ESCROW_ID 0x6 \\${NC}"
echo -e "     ${YELLOW}--gas-budget 100000000${NC}"
echo ""
echo "3. Or cancel the escrow (as sender):"
echo -e "   ${YELLOW}sui client call \\${NC}"
echo -e "     ${YELLOW}--package $PACKAGE_ID \\${NC}"
echo -e "     ${YELLOW}--module escrow \\${NC}"
echo -e "     ${YELLOW}--function cancel \\${NC}"
echo -e "     ${YELLOW}--type-args 0x2::sui::SUI \\${NC}"
echo -e "     ${YELLOW}--args $ESCROW_ID \\${NC}"
echo -e "     ${YELLOW}--gas-budget 100000000${NC}"
echo ""

# Offer to accept if sender is recipient
if [ "$SENDER" == "$RECIPIENT" ]; then
    echo ""
    read -p "You are both sender and recipient. Accept the escrow now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "Accepting escrow..."
        sui client call \
          --package "$PACKAGE_ID" \
          --module escrow \
          --function accept \
          --type-args "0x2::sui::SUI" \
          --args "$ESCROW_ID" "0x6" \
          --gas-budget 100000000

        echo ""
        echo -e "${GREEN}✅ Escrow accepted! Funds returned to your wallet.${NC}"
    fi
fi

echo ""
echo -e "${GREEN}🎉 Demo complete!${NC}"
