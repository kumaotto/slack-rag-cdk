import boto3
import re

bedrock_agent_runtime = boto3.client("bedrock-agent-runtime", region_name="us-east-1")


# 3秒以内にレスポンスを返す関数
def response_within_3sec(ack, body):
    # 3秒以内にレスポンスを返すために、ack()を呼び出す
    ack()


# Slackのイベントを処理する
def handle_app_mention_events(event, say, ack):
    ack()

    # メンションされたメッセージからメンション以降のテキストを取得
    input_text = re.sub(r"^<@(.+?)>", "", event["text"]).strip()
    
    # スレッドに返信するためのタイムスタンプを取得
    thread_ts = event["ts"] if event["ts"] else event["event_ts"]

    # Amazon Bedrockを使って応答テキストを生成
    result_response = generate_answer(input_text)

    # Slackに応答を返す
    say(
        channel=event["channel"],
        thread_ts=thread_ts,
        text=result_response
    )


# Amazon Bedrockを使って応答テキストを生成する
def generate_answer(input_text):

    # Bedrock用のシステムプロンプト
    prompt_template = """
        あなたは質問応答エージェントです。
        こちらから検索結果を提供しますので、ユーザーからの質問に対して、検索結果の情報だけを用いて回答してください。
        もし検索結果に質問の答えが見つからない場合は、「質問に対する正確な答えを見つけられませんでした」とお伝えください。
        ユーザーが主張する内容が正しいと断定せず、必ず検索結果で裏付けを確認してください。
        言語の指定がない場合は、日本語で回答してください。

        検索結果:
        $search_results$

        $output_format_instructions$
    """

    # Amazon Bedrock Knowledge Bases を呼び出す
    response = bedrock_agent_runtime.retrieve_and_generate(
        input={
            'text': input_text
        },
        retrieveAndGenerateConfiguration={
            'knowledgeBaseConfiguration': {
                "generationConfiguration": {
                    "promptTemplate": { 
                        "textPromptTemplate": prompt_template
                    },
                    "inferenceConfig": { 
                        "textInferenceConfig": { 
                            "maxTokens": 2048,
                            "stopSequences": ["Observation"],
                            "temperature": 0,
                            "topP": 1
                        }
                    },
                },
                "retrievalConfiguration": { 
                    "vectorSearchConfiguration": { 
                        "numberOfResults": 12,
                    }
                },
                'knowledgeBaseId': "S0VOH8TM0Y",
                'modelArn': "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
            },
            'type': 'KNOWLEDGE_BASE'
        }
    )

    response_body = response["output"]["text"]

    # citationsから参照情報を抽出
    citations = response.get("citations", [])
    reference_links = create_reference_links(citations)

    if not reference_links:
        reference_links = "参考文書が見つかりませんでした。"

    return reference_links + "\n\n" + response_body


# 参照情報からリンクを生成
def create_reference_links(citations):
    unique_references = set()

    for citation in citations:
        for reference in citation.get("retrievedReferences", []):
            title = reference["metadata"]["title"]
            url = reference["metadata"]["url"]
            unique_references.add((title, url))

    # 参照情報がない場合は空文字を返す
    if not unique_references:
        return ""
    
    # Slackのリンク形式の文字列を生成
    return "\n".join(f"・<{url}|{title}>" for title, url in unique_references)