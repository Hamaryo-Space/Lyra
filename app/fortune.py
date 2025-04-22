import random
import discord
from discord import app_commands

# 運勢コマンドを設定する関数
def setup_fortune_command(tree):
    # 今日の運勢コマンド
    @tree.command(name="今日の運勢", description="今日のあなたの運勢を占います")
    async def fortune(interaction: discord.Interaction):
        # 運勢のリスト
        fortunes = [
            '大吉：今日はとても幸運な日です！何をしても上手くいくでしょう。',
            '吉：良い一日になりそうです。ポジティブな気持ちで過ごしましょう。',
            '中吉：まずまずの運勢です。リラックスして過ごしましょう。',
            '小吉：小さな幸せが訪れるでしょう。細かいことに気を配りましょう。',
            '末吉：平凡な一日ですが、慎重に行動すれば問題ありません。',
            '凶：少し注意が必要な日です。慌てずに行動しましょう。',
            '大凶：今日は特に注意が必要です。無理はせず、静かに過ごしましょう。'
        ]
        
        # ランダムに運勢を選ぶ
        random_fortune = random.choice(fortunes)
        
        # リプライを送信
        await interaction.response.send_message(f'{interaction.user.mention}さんの今日の運勢は...\n**{random_fortune}**', silent=True)