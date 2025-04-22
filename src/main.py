import discord
import os
from discord import app_commands
from dotenv import load_dotenv

# 自作モジュールのインポート
from fortune import setup_fortune_command
from schedule import setup_schedule_command
from seminar import setup_seminar_command
from help import setup_help_command
from discord_rpc import LyraPresence
from unanimous_game import setup_unanimous_game_command
from server_stats import setup_server_stats_command  # 追加

# 環境変数の読み込み
load_dotenv()

# Botのインテントを設定
intents = discord.Intents.default()
intents.members = True  # メンバー情報取得のために必要
intents.presences = True  # プレゼンス情報取得のために必要
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
presence = LyraPresence(client)  # RPCインスタンスを作成


# Botが起動したときに実行される処理
@client.event
async def on_ready():
    print(f"{client.user} としてログインしました")
    # スラッシュコマンドをグローバルに同期
    await tree.sync()
    print("スラッシュコマンドを同期しました")

    # RPCステータスを設定
    await presence.set_simple_status("Bot")
    # または他の例:
    # await presence.update_activity_counter(len(client.guilds))
    # await presence.update_presence()
    print("ステータスを更新しました")


# 各コマンドの設定
setup_fortune_command(tree)
setup_schedule_command(tree)
setup_seminar_command(tree)
setup_help_command(tree)
setup_unanimous_game_command(tree)
setup_server_stats_command(tree)  # 追加

# Botを実行
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("エラー: DISCORD_TOKENが設定されていません")
    else:
        client.run(token)
