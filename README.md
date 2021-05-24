# PoC-Airflow-DiscordWebhookHook

This is a PoC to show that there is a small issue with the endpoint building on the `DiscordWebhookHook` class from the Airflow provider.

There are 2 tasks created:
- `send_new_message_task`: sends a Discord message using the new endpoint building on the `NewDiscordHook` class.
- `send_old_message_task`: sends a Discord message using the new endpoint building on the current `DiscordWebhookHook` class.

The way it is right now, the first task is gonna raise an exception:
```
requests.exceptions.HTTPError: 404 Client Error: Not Found for url: https://discord.com/api/webhooks/1/1
```
Just because it is an imaginary endpoint used just to fill the needs for this PoC.

The problem is the second task, which raises a different exception:
```
requests.exceptions.MissingSchema: Invalid URL 'webhooks/1/1': No schema supplied. Perhaps you meant http://webhooks/1/1?
```

This means that the endpoint is not being built correctly at all, since right now, it formatted as just `webhooks/{webhook.id}/{webhook.token}` instead of `https://discord.com/api/webhooks/{webhook.id}/{webhook.token}`

The new `return` on the `NewDiscordHook` class is just a suggestion, since it also solves the `http_conn_id` problem. Another way of solving this issue would be changing the regex to be something in the lines of `^https://discord.com/api/webhooks/[0-9]+/[a-zA-Z0-9_-]+$` and changing the documentation and `http_conn_id` handling also.