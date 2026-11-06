# Build the target Spring Boot application
Write-Host "Building target application..."
if (Test-Path ".\target_app") {
    Set-Location .\target_app
    mvn clean package -DskipTests
    Write-Host "Build complete. Artifact located in target/ directory."
} else {
    Write-Error "Directory .\target_app not found. Please ensure you are running the script from the project root."
    exit 1
}
