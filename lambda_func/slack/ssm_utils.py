import boto3

# SSMからパラメータを取得するクラス
class SSMUtils:
    def __init__(self):
        self.ssm_client = boto3.client('ssm')
        self.cache = {}

    # SSMからパラメータを取得する
    def get_parameter(self, parameter_name):
        # キャッシュにあればそれを返す
        if parameter_name in self.cache:
            return self.cache[parameter_name]

        # キャッシュになければSSMから取得する
        response = self.ssm_client.get_parameter(
            Name=parameter_name,
            WithDecryption=True
        )
        self.cache[parameter_name] = response['Parameter']['Value']
        return self.cache[parameter_name]
