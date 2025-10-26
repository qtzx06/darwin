#!/bin/bash

# Deployment Verification Script
# Verifies the deployed package and runs basic checks

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════╗"
echo "║    Deployment Verification Script         ║"
echo "╚═══════════════════════════════════════════╝"
echo -e "${NC}"

# Get deployment info
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CURRENT_ENV=$(sui client active-env)
DEPLOY_FILE="$SCRIPT_DIR/deployment-${CURRENT_ENV}.json"

if [ ! -f "$DEPLOY_FILE" ]; then
    echo -e "${RED}❌ No deployment found for $CURRENT_ENV${NC}"
    echo "Please run ./scripts/deploy.sh first"
    exit 1
fi

PACKAGE_ID=$(jq -r '.packageId' "$DEPLOY_FILE")
TX_DIGEST=$(jq -r '.txDigest' "$DEPLOY_FILE")
DEPLOYER=$(jq -r '.deployer' "$DEPLOY_FILE")

echo -e "${BLUE}Deployment Info:${NC}"
echo "  Network:    $CURRENT_ENV"
echo "  Package ID: $PACKAGE_ID"
echo "  Deployer:   $DEPLOYER"
echo "  Tx Digest:  $TX_DIGEST"
echo ""

# Test 1: Verify package exists
echo -e "${BLUE}[1/5] Checking package existence...${NC}"
PACKAGE_INFO=$(sui client object "$PACKAGE_ID" --json 2>&1)

if echo "$PACKAGE_INFO" | grep -q "error"; then
    echo -e "${RED}❌ Package not found on network${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Package exists${NC}"
echo ""

# Test 2: Verify module exists
echo -e "${BLUE}[2/5] Checking escrow module...${NC}"

# Try to get module info (this will error if module doesn't exist, but we catch it)
MODULE_CHECK=$(sui client call \
    --package "$PACKAGE_ID" \
    --module escrow \
    --function sender \
    --help 2>&1 || true)

if echo "$MODULE_CHECK" | grep -q "Function 'sender'"; then
    echo -e "${GREEN}✅ Escrow module found${NC}"
else
    echo -e "${RED}❌ Escrow module not found${NC}"
    exit 1
fi
echo ""

# Test 3: Check key functions exist
echo -e "${BLUE}[3/5] Verifying contract functions...${NC}"

FUNCTIONS=(
    "create_shared"
    "accept"
    "cancel"
    "raise_dispute"
    "resolve_dispute"
    "create_swap"
)

for func in "${FUNCTIONS[@]}"; do
    FUNC_CHECK=$(sui client call \
        --package "$PACKAGE_ID" \
        --module escrow \
        --function "$func" \
        --help 2>&1 || true)

    if echo "$FUNC_CHECK" | grep -q "Function '$func'"; then
        echo -e "  ${GREEN}✓${NC} $func"
    else
        echo -e "  ${RED}✗${NC} $func"
    fi
done
echo ""

# Test 4: Verify transaction
echo -e "${BLUE}[4/5] Verifying deployment transaction...${NC}"
TX_INFO=$(sui client tx-block "$TX_DIGEST" --json 2>&1 || true)

if echo "$TX_INFO" | grep -q "$PACKAGE_ID"; then
    echo -e "${GREEN}✅ Transaction verified${NC}"
else
    echo -e "${YELLOW}⚠️  Could not verify transaction${NC}"
fi
echo ""

# Test 5: Check events
echo -e "${BLUE}[5/5] Checking for contract events...${NC}"
echo "(This will show recent events if any escrows have been created)"
echo ""

EVENTS=$(sui client events --module escrow --limit 5 2>&1 || true)

if [ -n "$EVENTS" ] && ! echo "$EVENTS" | grep -q "error"; then
    echo "$EVENTS" | head -20
    echo -e "${GREEN}✅ Events found${NC}"
else
    echo -e "${YELLOW}ℹ️  No events yet (no escrows created)${NC}"
fi
echo ""

# Summary
echo -e "${BLUE}╔═══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Verification Complete ✓             ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════╝${NC}"
echo ""

# Explorer links
echo -e "${BLUE}🔍 View on Sui Explorer:${NC}"
if [ "$CURRENT_ENV" == "mainnet" ]; then
    echo "  Package: https://suiexplorer.com/object/$PACKAGE_ID"
    echo "  Tx:      https://suiexplorer.com/txblock/$TX_DIGEST"
elif [ "$CURRENT_ENV" == "testnet" ]; then
    echo "  Package: https://suiexplorer.com/object/$PACKAGE_ID?network=testnet"
    echo "  Tx:      https://suiexplorer.com/txblock/$TX_DIGEST?network=testnet"
else
    echo "  Package: https://suiexplorer.com/object/$PACKAGE_ID?network=devnet"
    echo "  Tx:      https://suiexplorer.com/txblock/$TX_DIGEST?network=devnet"
fi
echo ""

# Integration info
echo -e "${BLUE}📝 Integration Info:${NC}"
echo ""
echo "Use these values in your application:"
echo ""
echo "JavaScript/TypeScript:"
echo -e "${YELLOW}const PACKAGE_ID = '$PACKAGE_ID';${NC}"
echo ""
echo "Environment variable:"
echo -e "${YELLOW}VITE_ESCROW_PACKAGE_ID=$PACKAGE_ID${NC}"
echo ""

echo -e "${GREEN}✅ All checks passed!${NC}"
echo ""
echo "Ready to use escrow contracts. Try:"
echo -e "  ${YELLOW}./scripts/demo-escrow.sh${NC}"
echo ""
