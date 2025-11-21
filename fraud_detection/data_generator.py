import os
import time
import random
import csv

INPUT_DIR = "inputs"


def ensure_input_dir():
    if not os.path.exists(INPUT_DIR):
        os.makedirs(INPUT_DIR)


def generate_transaction_row(tx_id: int):
    amount = random.randint(500, 100000)  # 500 se 1,00,000 tak random amount
    timestamp = time.time()               # current UNIX timestamp
    return {
        "transaction_id": tx_id,
        "amount": amount,
        "timestamp": timestamp,
    }


def main():
    ensure_input_dir()
    tx_id = 1

    print("🔥 Data generator started... CSV files 'inputs/' folder me aa rahe hain.")

    while True:
        row = generate_transaction_row(tx_id)
        filename = os.path.join(INPUT_DIR, f"{time.time()}.csv")

        # Har file me header + 1 row
        with open(filename, mode="w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["transaction_id", "amount", "timestamp"],
            )
            writer.writeheader()
            writer.writerow(row)

        print(f"Generated: {row} -> {filename}")
        tx_id += 1
        time.sleep(1)  # 1 second baad next transaction


if __name__ == "__main__":
    main()
