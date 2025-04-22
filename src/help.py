import discord
from discord import app_commands


# ヘルプコマンドを設定する関数
def setup_help_command(tree):
    @tree.command(name="help", description="このBotの機能一覧を表示します")
    async def help_command(interaction: discord.Interaction):
        embed = discord.Embed(
            title="ゼミBot ヘルプ",
            description="このBotで利用できるコマンド一覧です",
            color=discord.Color.blue(),
        )

        # コマンド一覧を追加
        embed.add_field(
            name="/ゼミ日程",
            value="卒業研究Ⅰのゼミ日程を表示します\n"
            "オプション: `次回`(次回の予定のみ表示), `json`(JSONデータを表示)",
            inline=False,
        )

        embed.add_field(
            name="/年間行事",
            value="文教大学の年間行事予定を表示します\n"
            "オプション: `春学期`, `秋学期`(特定の学期のみ表示)",
            inline=False,
        )

        embed.add_field(
            name="/今日の運勢", value="今日のあなたの運勢を占います", inline=False
        )

        # 全員一致ゲームの説明を追加
        embed.add_field(
            name="/全員一致",
            value="全員一致ゲームを遊べます\n"
            "サブコマンド: `開始`(ゲームを開始), `ヘルプ`(遊び方の説明)",
            inline=False,
        )

        # サーバー統計コマンドの説明を追加
        embed.add_field(
            name="/サーバー",
            value="サーバーの統計情報を表示します\n"
            "サブコマンド: `統計`(サーバー全体の統計), `ユーザー`(特定ユーザーの情報)",
            inline=False,
        )

        embed.add_field(
            name="/help", value="このヘルプメッセージを表示します", inline=False
        )

        await interaction.response.send_message(embed=embed, silent=True)
