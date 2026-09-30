pipeline {
    agent any

    environment {
        DOCKER = "C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe"
        COMPOSE = "C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker-compose.exe"

        DB_NAME = "orders_db"
        DB_USER = "orders_user"
        DB_PASSWORD = "orders_password"
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }

        stage('Prepare Environment') {
            steps {
                echo 'Creating .env file for Docker Compose...'

                powershell '''
                    @"
DB_NAME=$env:DB_NAME
DB_USER=$env:DB_USER
DB_PASSWORD=$env:DB_PASSWORD
"@ | Set-Content .env
                '''
            }
        }

        stage('Build Order API Image') {
            steps {
                echo 'Building Order API Docker image...'

                bat '"%COMPOSE%" build order-api'
            }
        }

        stage('Start Complete Environment') {
            steps {
                echo 'Starting Nginx, Order API and PostgreSQL...'

                bat '"%COMPOSE%" up -d'
            }
        }

        stage('Wait for Services') {
            steps {
                echo 'Waiting for application...'

                powershell '''
                    $maxAttempts = 12

                    for ($i = 1; $i -le $maxAttempts; $i++) {
                        try {
                            $response = Invoke-RestMethod `
                                -Uri "http://localhost:8080/health" `
                                -Method Get `
                                -TimeoutSec 5

                            if ($response.status -eq "UP" -and $response.database -eq "CONNECTED") {
                                Write-Host "Application and database are healthy."
                                exit 0
                            }
                        }
                        catch {
                            Write-Host "Waiting for services... attempt $i"
                        }

                        Start-Sleep -Seconds 5
                    }

                    Write-Error "Application did not become healthy."
                    exit 1
                '''
            }
        }

        stage('Create Test Order') {
            steps {
                echo 'Creating test food order...'

                powershell '''
                    $body = @{
                        customer_name = "Jenkins"
                        food_item = "Pizza"
                        quantity = 2
                        price = 499
                    } | ConvertTo-Json

                    $response = Invoke-RestMethod `
                        -Uri "http://localhost:8080/orders" `
                        -Method Post `
                        -ContentType "application/json" `
                        -Body $body

                    Write-Host "Order response:"
                    $response | Format-List

                    if ($response.message -ne "Order created successfully") {
                        throw "Order creation failed."
                    }

                    "ORDER_ID=$($response.order_id)" | Set-Content order-result.txt
                '''
            }
        }

        stage('Retrieve Order') {
            steps {
                echo 'Retrieving orders...'

                powershell '''
                    $orders = Invoke-RestMethod `
                        -Uri "http://localhost:8080/orders" `
                        -Method Get

                    Write-Host "Orders returned by API:"
                    $orders | Format-Table

                    $orderId = (Get-Content order-result.txt).Split("=")[1]

                    $found = $orders | Where-Object {
                        $_.id -eq [int]$orderId
                    }

                    if (-not $found) {
                        throw "Created order was not found."
                    }

                    Write-Host "Created order found successfully."
                '''
            }
        }

        stage('Verify PostgreSQL') {
            steps {
                echo 'Verifying order directly in PostgreSQL...'

                powershell '''
                    $orderId = (Get-Content order-result.txt).Split("=")[1]

                    $result = & "$env:COMPOSE" exec -T db `
                        psql -U "$env:DB_USER" `
                        -d "$env:DB_NAME" `
                        -t -A `
                        -c "SELECT COUNT(*) FROM orders WHERE id = $orderId;"

                    $result = $result.Trim()

                    Write-Host "Database verification result: $result"

                    if ($result -ne "1") {
                        throw "Order was not found in PostgreSQL."
                    }

                    Write-Host "Order successfully verified in PostgreSQL."
                '''
            }
        }

        stage('Show Status') {
            steps {
                echo 'Displaying container status...'

                bat '"%COMPOSE%" ps'
            }
        }
    }

    post {

        failure {
            echo 'Pipeline failed. Displaying useful container logs...'

            bat '"%COMPOSE%" logs --no-color db order-api nginx'
        }

        always {
            echo 'Stopping application containers...'

            bat '"%COMPOSE%" down'
        }
    }
}