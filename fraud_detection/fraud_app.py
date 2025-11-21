import pathway as pw

# 1. Schema
class TransactionSchema(pw.Schema):
    transaction_id: int
    amount: int
    timestamp: float


# 2. Read from 'inputs/' directory in STREAMING mode
transactions = pw.io.csv.read(
    "./inputs/",            # folder jahan generator CSV files daal raha hai
    schema=TransactionSchema,
    autocommit_duration_ms=1000,
)


# 3. Fraud logic – simple rule on amount
def fraud_detection_logic(amount: int) -> str:
    if amount > 30000:
        return "Fraudulent"
    else:
        return "Normal"


# 4. Results table
results = transactions.select(
    transaction_id=transactions.transaction_id,
    amount=transactions.amount,
    timestamp=transactions.timestamp,
    fraud_result=pw.apply(fraud_detection_logic, transactions.amount),
)


# 5. File output – saara result yahan aaega
pw.io.jsonlines.write(results, "output.jsonl")


# 6. Run – yeh stream ko continuously process karega
if __name__ == "__main__":
    pw.run()
