#!/bin/bash
# build-and-publish.sh
# E14 Oracle — Docker Hub Publication Script
# Builds, tags, and pushes images to Docker Hub

set -e

# Configuration
DOCKER_HUB_USERNAME="${DOCKER_HUB_USERNAME:-your-docker-hub-username}"
IMAGE_NAME="e14-oracle"
MAJOR_VERSION="1"
MINOR_VERSION="0"
FULL_VERSION="${MAJOR_VERSION}.${MINOR_VERSION}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${YELLOW}[1/5]${NC} Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}ERROR: Docker is not installed${NC}"
    exit 1
fi

if [ -z "$DOCKER_HUB_USERNAME" ] || [ "$DOCKER_HUB_USERNAME" == "your-docker-hub-username" ]; then
    echo -e "${RED}ERROR: DOCKER_HUB_USERNAME not set${NC}"
    echo "Usage: DOCKER_HUB_USERNAME=myusername ./build-and-publish.sh"
    exit 1
fi

# Build local image
echo -e "${YELLOW}[2/5]${NC} Building Docker image..."
docker build -t ${IMAGE_NAME}:${FULL_VERSION} -f Dockerfile .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Build successful${NC}"
else
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi

# Tag for Docker Hub
echo -e "${YELLOW}[3/5]${NC} Tagging image for Docker Hub..."
docker tag ${IMAGE_NAME}:${FULL_VERSION} ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${FULL_VERSION}
docker tag ${IMAGE_NAME}:${FULL_VERSION} ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:latest

echo -e "${GREEN}✓ Tagged successfully${NC}"

# Login check
echo -e "${YELLOW}[4/5]${NC} Checking Docker Hub authentication..."
if ! docker info | grep -q "Username"; then
    echo -e "${YELLOW}Not logged in to Docker Hub. Running: docker login${NC}"
    docker login
fi

# Push to Docker Hub
echo -e "${YELLOW}[5/5]${NC} Pushing to Docker Hub..."
docker push ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${FULL_VERSION}
docker push ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:latest

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Push successful${NC}"
    echo ""
    echo -e "${GREEN}=== PUBLICATION COMPLETE ===${NC}"
    echo ""
    echo "Images published to Docker Hub:"
    echo "  - ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${FULL_VERSION}"
    echo "  - ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:latest"
    echo ""
    echo "Pull with:"
    echo "  docker pull ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:latest"
    echo ""
else
    echo -e "${RED}✗ Push failed${NC}"
    exit 1
fi
