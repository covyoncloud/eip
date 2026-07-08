import boto3, json, os
sfn = boto3.client("stepfunctions")
STATE_MACHINE_ARN = os.environ["STATE_MACHINE_ARN"]

def handler(event, context):
    failures = []
    for record in event["Records"]:
        try:
            s3_event = json.loads(record["body"])
            if "Records" not in s3_event:
                continue
            for s3_rec in s3_event["Records"]:
                sfn.start_execution(
                    stateMachineArn=STATE_MACHINE_ARN,
                    input=json.dumps({
                        "bucket": s3_rec["s3"]["bucket"]["name"],
                        "key": s3_rec["s3"]["object"]["key"],
                    }),
                )
                print(f"exécution démarrée pour {s3_rec['s3']['object']['key']}")
        except Exception as e:
            print(f"ÉCHEC {record['messageId']}: {e}")
            failures.append({"itemIdentifier": record["messageId"]})
    return {"batchItemFailures": failures}