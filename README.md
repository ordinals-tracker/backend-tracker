# Ordinals Tax Report - Backend Application

## Overview

Backend repository for Bounty #8 under the OMBounties program. This bounty aims to create an Ordinals Tax Reporting system. The system is designed to generate Profit & Loss (PNL) statements by pulling Partially Signed Bitcoin Transactions (PSBT) from Bitcoin wallets and referencing the BTC price at the time each PSBT occurred

## Features

- Healthcheck: Checks if the application is running.
- Track Wallets: Retrieves activity for specified wallets.
- Holdings: Retrieves holdings, total balance, and USD total balance for specified wallets.

## Endpoints

- `GET /`: Healthcheck
- `GET /track/<wallets>`: Get all data related to the specified wallets.
- `GET /holdings/<wallets>`: Get all holdings for the specified wallets.

## Requirements

Python >=3.1 and Flask are required to run this application.

## Installation

1. Clone this repository.
    ```bash
    git clone <repository_url>
    ```
2. Navigate to the project directory.
    ```bash
    cd <project_directory>
    ```
3. Install the required packages.
    ```bash
    pip install -r requirements.txt
    ```

## Setting Up API Key for Magic Eden

1. Go to https://docs.magiceden.io/reference/ordinals-overview and get an API Key.
2. Open the `utils.py` file.
3. Locate the variable `ME_TOKEN` and set it to your Magic Eden API key.
    ```python
    ME_TOKEN = "your_magic_eden_api_key_here"
    ```

## Running the Application

Run the application using the following command:

```bash
python application.py
