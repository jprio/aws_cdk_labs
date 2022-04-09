import boto3


def main(event, context):
    dynamodb = boto3.resource("dynamodb")

    table = dynamodb.Table('my-table')
    response = table.put_item(
        Item={
            'id': "1989",
            'title': "plop",
            'info': {
                'plot': "p",
                'rating': "rating"
            }
        }
    )


main(None, None)
