#!/bin/bash

# Escrow Contracts Deployment Script
# Automates building, testing, and deploying to Sui blockchain

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════╗"
echo "║   Escrow Contracts Deployment Script     ║"
echo "║            Sui Blockchain                 ║"
echo "╚═══════════════════════════════════════════╝"
echo -e "${NC}"

# Check if sui CLI is installed
if ! command -v sui &> /dev/null; then
    echo -e "${RED}❌ Error: sui CLI not found${NC}"
    echo ""
    echo "Please install Sui CLI first:"
    echo "  cargo install --locked --git https://github.com/MystenLabs/sui.git --branch main sui"
    echo ""
    echo "Or visit: https://docs.sui.io/guides/developer/getting-started/sui-install"
    exit 1
fi

echo -e "${GREEN}✅ Sui CLI found: $(sui --version)${NC}"
echo ""

# Get current network
CURRENT_ENV=$(sui client active-env 2>/dev/null || echo "unknown")
CURRENT_ADDR=$(sui client active-address 2>/dev/null || echo "unknown")

echo -e "${BLUE}📡 Current Configuration:${NC}"
echo "   Network: $CURRENT_ENV"
echo "   Address: $CURRENT_ADDR"
echo ""

# Ask for network selection
echo -e "${YELLOW}Select deployment network:${NC}"
echo "1) devnet (recommended for testing)"
echo "2) testnet"
echo "3) mainnet (production)"
echo "4) Use current network ($CURRENT_ENV)"
echo ""
read -p "Enter choice [1-4]: " network_choice

case $network_choice in
    1)
        TARGET_ENV="devnet"
        sui client switch --env devnet
        ;;
    2)
        TARGET_ENV="testnet"
        sui client switch --env testnet
        ;;
    3)
        TARGET_ENV="mainnet"
        echo -e "${RED}⚠️  WARNING: You are deploying to MAINNET!${NC}"
        read -p "Are you absolutely sure? (type 'YES' to confirm): " confirm
        if [ "$confirm" != "YES" ]; then
            echo "Deployment cancelled."
            exit 0
        fi
        sui client switch --env mainnet
        ;;
    4)
        TARGET_ENV=$CURRENT_ENV
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ Target network: $TARGET_ENV${NC}"
echo ""

# Check gas balance
echo -e "${BLUE}💰 Checking gas balance...${NC}"
GAS_BALANCE=$(sui client gas --json 2>/dev/null | head -1 || echo "[]")

if [ "$GAS_BALANCE" == "[]" ]; then
    echo -e "${RED}❌ No gas coins found!${NC}"

    if [ "$TARGET_ENV" == "devnet" ] || [ "$TARGET_ENV" == "testnet" ]; then
        echo ""
        echo "Getting test tokens from faucet..."
        sui client faucet
        echo -e "${GREEN}✅ Test tokens received${NC}"
    else
        echo ""
        echo "Please fund your wallet with SUI tokens and try again."
        exit 1
    fi
fi

echo -e "${GREEN}✅ Gas balance OK${NC}"
echo ""

# Navigate to project directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo -e "${BLUE}📂 Project directory: $PROJECT_DIR${NC}"
echo ""

# Run tests first
echo -e "${BLUE}🧪 Running tests...${NC}"
sui move test

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Tests failed! Please fix errors before deploying.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All tests passed!${NC}"
echo ""

# Build the package
echo -e "${BLUE}🔨 Building Move package...${NC}"
sui move build

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build failed!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build successful${NC}"
echo ""

# Confirm deployment
echo -e "${YELLOW}Ready to deploy to $TARGET_ENV${NC}"
read -p "Continue with deployment? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

# Deploy the package
echo ""
echo -e "${BLUE}📦 Publishing package to $TARGET_ENV...${NC}"
echo "This may take a moment..."
echo ""

PUBLISH_OUTPUT=$(sui client publish --gas-budget 200000000 --json 2>&1)

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Publish failed!${NC}"
    echo "$PUBLISH_OUTPUT"
    exit 1
fi

# Parse the output
PACKAGE_ID=$(echo "$PUBLISH_OUTPUT" | jq -r '.objectChanges[] | select(.type=="published") | .packageId' 2>/dev/null)

if [ -z "$PACKAGE_ID" ] || [ "$PACKAGE_ID" == "null" ]; then
    echo -e "${RED}❌ Could not extract Package ID from publish output${NC}"
    echo "Raw output:"
    echo "$PUBLISH_OUTPUT"
    exit 1
fi

# Get transaction digest
TX_DIGEST=$(echo "$PUBLISH_OUTPUT" | jq -r '.digest' 2>/dev/null)

echo -e "${GREEN}✅ Package published successfully!${NC}"
echo ""

# Display results
echo -e "${BLUE}╔═══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Deployment Successful! 🎉         ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Network:${NC}     $TARGET_ENV"
echo -e "${GREEN}Package ID:${NC}  $PACKAGE_ID"
echo -e "${GREEN}Tx Digest:${NC}   $TX_DIGEST"
echo ""

# Save deployment info
DEPLOY_FILE="scripts/deployment-${TARGET_ENV}.json"
cat > "$DEPLOY_FILE" << EOF
{
  "network": "$TARGET_ENV",
  "packageId": "$PACKAGE_ID",
  "txDigest": "$TX_DIGEST",
  "deployer": "$CURRENT_ADDR",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "version": "1.0.0"
}
EOF

echo -e "${GREEN}✅ Deployment info saved to: $DEPLOY_FILE${NC}"
echo ""

# Create .env file
ENV_FILE="../.env.escrow"
cat > "$ENV_FILE" << EOF
# Escrow Contracts Configuration
# Generated on $(date)

# Network
VITE_ESCROW_NETWORK=$TARGET_ENV

# Contract Address
VITE_ESCROW_PACKAGE_ID=$PACKAGE_ID

# Transaction Digest
VITE_ESCROW_TX_DIGEST=$TX_DIGEST

# Deployer Address
VITE_ESCROW_DEPLOYER=$CURRENT_ADDR
EOF

echo -e "${GREEN}✅ Environment file created: $ENV_FILE${NC}"
echo ""

# Show next steps
echo -e "${BLUE}📝 Next Steps:${NC}"
echo ""
echo "1. Save the Package ID for your application:"
echo -e "   ${YELLOW}$PACKAGE_ID${NC}"
echo ""
echo "2. View the deployment on Sui Explorer:"
if [ "$TARGET_ENV" == "mainnet" ]; then
    echo -e "   ${BLUE}https://suiexplorer.com/object/$PACKAGE_ID${NC}"
elif [ "$TARGET_ENV" == "testnet" ]; then
    echo -e "   ${BLUE}https://suiexplorer.com/object/$PACKAGE_ID?network=testnet${NC}"
else
    echo -e "   ${BLUE}https://suiexplorer.com/object/$PACKAGE_ID?network=devnet${NC}"
fi
echo ""
echo "3. Try creating an escrow:"
echo -e "   ${YELLOW}./scripts/demo-escrow.sh${NC}"
echo ""
echo "4. Update your frontend configuration:"
echo -e "   ${YELLOW}cp ../.env.escrow ../src/config/escrow.js${NC}"
echo ""

# Offer to run demo
read -p "Would you like to run a demo escrow now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "scripts/demo-escrow.sh" ]; then
        ./scripts/demo-escrow.sh
    else
        echo "Demo script not found. Please create it manually."
    fi
fi

echo ""
echo -e "${GREEN}🎉 Deployment complete!${NC}"
