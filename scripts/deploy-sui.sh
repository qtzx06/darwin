#!/bin/bash

# Sui Colosseum Deployment Script
# This script helps automate the deployment process

set -e  # Exit on error

echo "🎮 Colosseum Betting - Sui Deployment Script"
echo "=============================================="
echo ""

# Check if sui CLI is installed
if ! command -v sui &> /dev/null; then
    echo "❌ Error: sui CLI not found"
    echo "Please install Sui CLI first:"
    echo "cargo install --locked --git https://github.com/MystenLabs/sui.git --branch main sui"
    exit 1
fi

# Check current network
CURRENT_ENV=$(sui client active-env)
echo "📡 Current Sui environment: $CURRENT_ENV"
echo ""

# Confirm before proceeding
read -p "Continue deployment on $CURRENT_ENV? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

# Build the Move package
echo ""
echo "🔨 Building Move package..."
cd colosseum
sui move build

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi

echo "✅ Build successful"
echo ""

# Publish the package
echo "📦 Publishing package to $CURRENT_ENV..."
echo "This may take a moment..."
echo ""

PUBLISH_OUTPUT=$(sui client publish --gas-budget 200000000 --json)

if [ $? -ne 0 ]; then
    echo "❌ Publish failed"
    exit 1
fi

# Extract Package ID
PACKAGE_ID=$(echo $PUBLISH_OUTPUT | jq -r '.objectChanges[] | select(.type=="published") | .packageId')

if [ -z "$PACKAGE_ID" ]; then
    echo "❌ Could not extract Package ID from publish output"
    echo "Raw output:"
    echo "$PUBLISH_OUTPUT"
    exit 1
fi

echo "✅ Package published successfully!"
echo "📦 Package ID: $PACKAGE_ID"
echo ""

# Extract House Object ID (created by init function)
HOUSE_ID=$(echo $PUBLISH_OUTPUT | jq -r '.objectChanges[] | select(.objectType | contains("::colosseum_bets::House")) | .objectId')

if [ -z "$HOUSE_ID" ]; then
    echo "⚠️  Could not automatically extract House ID"
    echo "Please find it manually from the publish output above"
else
    echo "🏠 House Object ID: $HOUSE_ID"
fi

echo ""
echo "================================================"
echo "✨ Deployment Summary"
echo "================================================"
echo "Network:    $CURRENT_ENV"
echo "Package ID: $PACKAGE_ID"
echo "House ID:   $HOUSE_ID"
echo ""
echo "📝 Next steps:"
echo "1. Update your .env file with these values:"
echo "   VITE_SUI_NETWORK=$CURRENT_ENV"
echo "   VITE_SUI_PACKAGE_ID=$PACKAGE_ID"
echo "   VITE_SUI_HOUSE_ID=$HOUSE_ID"
echo ""
echo "2. (Optional) Seed the house pot:"
echo "   sui client split-coin --coin-id <YOUR_COIN_ID> --amounts 10000000000 --gas-budget 100000000"
echo "   sui client call --package $PACKAGE_ID --module colosseum_bets --function deposit --args $HOUSE_ID <SPLIT_COIN_ID> --gas-budget 100000000"
echo ""
echo "3. Restart your dev server:"
echo "   npm run dev"
echo ""
echo "🎉 Deployment complete!"
