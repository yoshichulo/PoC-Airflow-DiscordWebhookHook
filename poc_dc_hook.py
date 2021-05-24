import re
import requests
from typing import Any, Dict, Optional

import airflow
from airflow import DAG
from airflow.exceptions import AirflowException
from airflow.providers.http.hooks.http import HttpHook
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
from airflow.providers.discord.hooks.discord_webhook import DiscordWebhookHook


class NewDiscordHook(DiscordWebhookHook):
    def _get_webhook_endpoint(self, http_conn_id: Optional[str], webhook_endpoint: Optional[str]) -> str:
        """
        Given a Discord http_conn_id, return the default webhook endpoint or override if a
        webhook_endpoint is manually supplied.

        :param http_conn_id: The provided connection ID
        :param webhook_endpoint: The manually provided webhook endpoint
        :return: Webhook endpoint (str) to use
        """
        if webhook_endpoint:
            endpoint = webhook_endpoint
        elif http_conn_id:
            conn = self.get_connection(http_conn_id)
            extra = conn.extra_dejson
            endpoint = extra.get('webhook_endpoint', '')
        else:
            raise AirflowException(
                'Cannot get webhook endpoint: No valid Discord webhook endpoint or http_conn_id supplied.'
            )

        # make sure endpoint matches the expected Discord webhook format
        if not re.match('^webhooks/[0-9]+/[a-zA-Z0-9_-]+$', endpoint):
            raise AirflowException(
                'Expected Discord webhook endpoint in the form of "webhooks/{webhook.id}/{webhook.token}".'
            )

        # This is the only line that changed in the original code
        return f'https://discord.com/api/{endpoint}'


with DAG(
    dag_id='poc_dc_hook_dag',
    default_args={},
    schedule_interval=None,
    start_date=days_ago(1),
    tags=['poc'],
) as poc_dc_hook_dag:

    def send_new_message():
        discord_hook = NewDiscordHook(webhook_endpoint='webhooks/1/1')
        discord_hook.message = "Test"

        discord_hook.execute()
    
    def send_old_message():
        discord_hook = DiscordWebhookHook(webhook_endpoint='webhooks/1/1')
        discord_hook.message = "Test"

        discord_hook.execute()

    send_new_message_task = PythonOperator(
        task_id='send_new_message_task',
        python_callable=send_new_message
    )

    send_old_message_task = PythonOperator(
        task_id='send_old_message_task',
        python_callable=send_old_message,
        trigger_rule='all_done'
    )

    send_new_message_task >> send_old_message_task

