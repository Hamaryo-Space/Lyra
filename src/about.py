import discord
from discord import app_commands
import os
import json
from datetime import datetime


class AboutCommands:
    def __init__(self):
        # Botの説明文
        self.bot_description = """

このBotはゼミグループ用に開発された専用Botです。
ゼミ日程の管理、ミニゲーム、サーバー統計など様々な機能を提供します。

**【主な機能】**
• ゼミ日程の表示と管理
• 大学の年間行事予定の表示
• サーバー統計情報の表示（※動作未確認）
• 運勢占い
• 全員一致ゲーム（※動作未確認）
• 問い合わせ機能（開発者へのDM送信）

**【問い合わせ先】**
バグ報告や機能提案がございましたら、開発者 <@742627994958561302> までご連絡ください。

**【開発情報】**
開発: Hamaryo-Space
ライセンス: MIT
"""

    # Botについてのコマンド
    async def about_bot(self, interaction: discord.Interaction):
        """Botの紹介と問い合わせ先を表示します"""
        embed = discord.Embed(
            title="Lyra - ゼミグループ専用Bot",
            description=self.bot_description,
            color=discord.Color.blue(),
        )

        # Botのアイコンがあれば設定
        if interaction.client.user.avatar:
            embed.set_thumbnail(url=interaction.client.user.avatar.url)

        # バージョン情報などの追加情報
        try:
            # 設定ファイルがあればバージョン情報を読み込む
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, "config.json")
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                if "version" in config:
                    embed.add_field(
                        name="バージョン", value=f"v{config['version']}", inline=True
                    )
        except:
            pass

        # サーバー数
        try:
            guild_count = len(interaction.client.guilds)
            embed.add_field(
                name="導入サーバー数", value=f"{guild_count}サーバー", inline=True
            )
        except:
            pass

        # 稼働時間
        try:
            from discord_rpc import LyraPresence

            for module in globals().values():
                if isinstance(module, LyraPresence):
                    uptime = datetime.utcnow() - module.start_time
                    days = uptime.days
                    hours, remainder = divmod(uptime.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    embed.add_field(
                        name="稼働時間",
                        value=f"{days}日 {hours}時間 {minutes}分",
                        inline=True,
                    )
                    break
        except:
            pass

        # フッター（クリック可能なリンク）
        embed.description += (
            "\n\n[GitHub リポジトリ](https://github.com/Hamaryo-Space/Lyra)"
        )
        embed.set_footer(text="Developed by Hamaryo-Space")

        await interaction.response.send_message(embed=embed, silent=True)

    # 開発者への問い合わせコマンド - クラス内に移動
    async def contact_developer(
        self, interaction: discord.Interaction, メッセージ: str
    ):
        """開発者への問い合わせや機能提案を送信します"""
        embed = discord.Embed(
            title="問い合わせ内容を送信しました",
            description=f"以下の内容で開発者 <@742627994958561302> に通知されます。返信をお待ちください。",
            color=discord.Color.green(),
        )

        embed.add_field(name="メッセージ", value=メッセージ, inline=False)

        embed.add_field(
            name="送信者情報",
            value=f"名前: {interaction.user.name}\nID: {interaction.user.id}",
            inline=False,
        )

        embed.set_footer(
            text="問い合わせ時刻: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        # ユーザーに確認メッセージを送信
        await interaction.response.send_message(embed=embed, ephemeral=True)

        # 開発者にDMを送信
        try:
            # 開発者のIDを指定
            developer_id = 742627994958561302
            developer_user = await interaction.client.fetch_user(developer_id)

            # 開発者へのDM用Embed作成
            dev_embed = discord.Embed(
                title="新しい問い合わせが届きました",
                description="Botを通じて新しい問い合わせが届きました。",
                color=discord.Color.blue(),
                timestamp=datetime.now(),
            )

            # 問い合わせ内容を追加
            dev_embed.add_field(name="メッセージ内容", value=メッセージ, inline=False)

            # 送信者の情報
            dev_embed.add_field(
                name="送信者情報",
                value=f"名前: {interaction.user.name}\n"
                f"ID: {interaction.user.id}\n"
                f"サーバー: {interaction.guild.name if interaction.guild else 'DM'}\n"
                f"チャンネル: {interaction.channel.name if interaction.channel else 'N/A'}",
                inline=False,
            )

            # 返信用の情報
            dev_embed.add_field(
                name="返信方法",
                value=f"返信する場合はDMで `{interaction.user.name}` さん（ID: {interaction.user.id}）にメッセージを送信してください。",
                inline=False,
            )

            # 送信者のアイコンがあれば設定
            if interaction.user.avatar:
                dev_embed.set_thumbnail(url=interaction.user.avatar.url)

            # フッター
            dev_embed.set_footer(text="Lyra Bot - 問い合わせシステム")

            # DMを送信
            await developer_user.send(embed=dev_embed)

            # 管理用チャンネルにもログを残す場合（オプション）
            # log_channel_id = 管理用チャンネルID
            # log_channel = interaction.client.get_channel(log_channel_id)
            # if log_channel:
            #     await log_channel.send(embed=dev_embed)

        except Exception as e:
            # DMの送信に失敗した場合のエラーログ
            print(f"開発者へのDM送信に失敗しました: {e}")

            # 失敗通知をユーザーに送信する場合（オプション）
            try:
                await interaction.followup.send(
                    "開発者への通知送信中にエラーが発生しました。別の方法でお問い合わせください。",
                    ephemeral=True,
                )
            except:
                pass


# コマンド設定関数
def setup_about_commands(tree):
    about_commands = AboutCommands()

    # Botの紹介コマンドグループ
    about_group = app_commands.Group(name="bot", description="Botに関する情報コマンド")

    @about_group.command(name="紹介", description="Botの紹介と問い合わせ先を表示します")
    async def about(interaction: discord.Interaction):
        await about_commands.about_bot(interaction)

    @about_group.command(
        name="問い合わせ", description="開発者への問い合わせや機能提案を送信します"
    )
    @app_commands.describe(メッセージ="開発者に送信するメッセージ内容")
    async def contact(interaction: discord.Interaction, メッセージ: str):
        await about_commands.contact_developer(interaction, メッセージ)

    tree.add_command(about_group)
