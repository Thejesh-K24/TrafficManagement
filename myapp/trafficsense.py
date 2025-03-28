import boto3

class TrafficSense:
    def __init__(self, table_name, sns_topic_arn):
        """
        Initialize TrafficSense with AWS DynamoDB and SNS.
        :param table_name: Name of the DynamoDB table
        :param sns_topic_arn: ARN of the SNS topic
        """
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(TrafficUpdate)
        self.sns = boto3.client('sns')
        self.sns_topic_arn = sns_topic_arn

    def calculate_signal_time(self, vehicle_count):
        """
        Calculate signal time based on vehicle count.
        :param vehicle_count: Number of vehicles at the junction
        :return: Signal time in seconds
        """
        if vehicle_count < 10:
            return 10  # Green for 10 seconds
        elif vehicle_count < 30:
            return 30  # Green for 30 seconds
        else:
            return 60  # Green for 60 seconds

    def update_traffic(self, junction_id, vehicle_count):
        """
        Update the traffic data in DynamoDB and send SNS notifications.
        :param junction_id: Unique identifier for the junction
        :param vehicle_count: Number of vehicles detected at the junction
        :return: Dictionary with traffic data update details
        """
        signal_time = self.calculate_signal_time(vehicle_count)

        # Update DynamoDB
        self.table.put_item(Item={
            'junction_id': junction_id,
            'vehicle_count': vehicle_count,
            'signal_time': signal_time
        })

         # Prepare SNS Message
        message = {
                "junction_id": junction_id,
                "number_of_vehicles": number_of_vehicles,
                "signal_time": signal_time
            }
        self.sns_client.publish(
                TopicArn=self.sns_topic_arn,
                Message=json.dumps(message),
                Subject="Traffic Update Notification"
            )

        return {"status": "success", "signal_time": signal_time}
