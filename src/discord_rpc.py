import discord
from datetime import datetime, timedelta


# Discord RPCを設定するためのクラス
class LyraPresence:
    def __init__(self, client):
        self.client = client
        self.start_time = datetime.utcnow()

    # Botのステータスを更新する関数
    async def update_presence(self):
        """Botのステータス（Rich Presence）を更新します"""
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="ゼミの予定",
            details="ゼミ関連の情報を管理しています",
            start=self.start_time,
            assets={
                "large_image": "icon",  # Discordの開発者ポータルでアップロードした画像のID
                "large_text": "Lyra Bot",
                "small_image": "status_online",
                "small_text": "オンライン",
            },
            buttons=[
                {
                    "label": "コマンド一覧",
                    "url": "https://github.com/Hamaryo-Space/Lyra",
                }
            ],
        )

        await self.client.change_presence(activity=activity)

    # Botのアクティビティカウンターを更新する関数
    async def update_activity_counter(self, guild_count):
        """サーバー数に基づいてステータスを更新します"""
        await self.client.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{guild_count}つのサーバーで稼働中",
            )
        )

    # シンプルなステータスに更新する関数
    async def set_simple_status(self, status_text):
        """シンプルなテキストステータスを設定します"""
        await self.client.change_presence(activity=discord.Game(name=status_text))

    # シンプルなステータスに更新する関数
    async def now_status(self, status_text):
        """シンプルなテキストステータスを設定します"""
        await self.client.change_presence(activity=discord.Game(name=status_text))
