#!/bin/bash

echo "Starting ChainOps AI - Multi-Agent Supply Chain Risk Intelligence Platform"
echo

echo "Installing dependencies..."
npm run install-all

echo
echo "Starting ChainOps AI..."
echo "Backend will run on http://localhost:8000"
echo "Frontend will run on http://localhost:3000"
echo

npm run dev
