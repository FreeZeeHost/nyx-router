#!/bin/bash
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo "${GREEN}✅ $1${NC}"; }
print_error() { echo "${RED}❌ $1${NC}"; }
print_warning() { echo "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo "${BLUE}ℹ️  $1${NC}"; }
