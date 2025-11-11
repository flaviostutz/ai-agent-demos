#!/bin/bash

# Loan Application System Startup Script
# This script starts both the backend API and frontend web application

set -e

echo "🚀 Starting Loan Application System..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backend is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️  Backend API already running on port 8000${NC}"
else
    echo -e "${BLUE}📡 Starting Backend API...${NC}"
    cd "$(dirname "$0")"
    make run &
    BACKEND_PID=$!
    echo -e "${GREEN}✓ Backend API starting (PID: $BACKEND_PID)${NC}"
    echo "   API will be available at: http://localhost:8000"
    echo "   Swagger docs at: http://localhost:8000/docs"
fi

# Wait a moment for backend to start
sleep 3

# Check if frontend is already running
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️  Frontend already running on port 3000${NC}"
else
    echo ""
    echo -e "${BLUE}🌐 Starting Frontend...${NC}"
    cd "$(dirname "$0")/frontend"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}📦 Installing frontend dependencies (first time)...${NC}"
        make install
    fi
    
    make dev &
    FRONTEND_PID=$!
    echo -e "${GREEN}✓ Frontend starting (PID: $FRONTEND_PID)${NC}"
    echo "   Frontend will be available at: http://localhost:3000"
fi

echo ""
echo -e "${GREEN}✨ System is starting up!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📋 Access Points:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🌐 Web Application:  http://localhost:3000"
echo "  📡 API Backend:      http://localhost:8000"
echo "  📚 API Docs:         http://localhost:8000/docs"
echo "  🏥 Health Check:     http://localhost:8000/health"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 Tip: Press Ctrl+C to stop all services"
echo ""

# Wait for user interrupt
wait
