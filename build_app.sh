#!/bin/bash

# Build the target Spring Boot application
echo "Building target application..."
cd ./target_app
mvn clean package -DskipTests

echo "Build complete. Artifact located in target/ directory."
