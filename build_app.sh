#!/bin/bash

# Build the target Spring Boot application
echo "Building target application..."
cd /mnt/c/Users/jsoehner/harness_project/target_app
mvn clean package -DskipTests

echo "Build complete. Artifact located in target/ directory."
