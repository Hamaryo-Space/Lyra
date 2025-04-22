import discord
from discord import app_commands
import random
from datetime import datetime


# ゲームの状態を管理するクラス
class UnanimousGame:
    def __init__(self):
        self.active_games = {}  # サーバーごとのゲーム状態を管理
        self.default_topics = [
            "好きな食べ物は？",
            "気分転換に何をする？",
            "朝起きて最初にすることは？",
            "理想のデートスポットは？",
            "休日の過ごし方は？",
            "好きな季節は？",
            "好きな映画のジャンルは？",
            "好きな飲み物は？",
            "好きな色は？",
            "好きな動物は？",
            "最近買った物は？",
            "将来住みたい場所は？",
            "もし無人島に一つだけ持っていくなら？",
            "好きなゲームは？",
            "好きな音楽のジャンルは？",
        ]

        # ゲーム説明文
        self.game_description = """
**【全員一致ゲーム】**
「以心伝心ゲーム」や「意志疎通ゲーム」とも呼ばれるパーティーゲームです。
お題に対して、全員が同じ回答をすることを目指します。

**【遊び方】**
1. `/全員一致 開始` でゲームを開始
2. GMがお題を決定します
3. 参加者全員がDMで回答を送信
4. 全員の回答が集まったら結果を発表

**【勝敗条件】**
- 回答が全員一致したら全員の勝利
- 一致しなければ全員の負け
"""

    # ゲームを作成する
    async def create_game(self, interaction, topic=None):
        guild_id = interaction.guild_id

        # すでにゲームが進行中の場合
        if guild_id in self.active_games:
            await interaction.response.send_message(
                "すでにゲームが進行中です！", ephemeral=True
            )
            return

        # GMをゲーム作成者に設定
        gm = interaction.user

        # トピックが指定されていない場合はランダムに選択
        if not topic:
            topic = random.choice(self.default_topics)

        # ゲーム情報を作成
        self.active_games[guild_id] = {
            "gm": gm,
            "topic": topic,
            "channel": interaction.channel,
            "participants": {},
            "answers": {},
            "status": "waiting",  # waiting, collecting_answers, completed
            "start_time": datetime.now(),
            "consecutive_wins": 0,
        }

        # ボタン付きメッセージを作成
        embed = discord.Embed(
            title="🎮 全員一致ゲーム",
            description=f"**GMは {gm.mention} です**\n\n**お題**: {topic}\n\n参加者はボタンを押して参加しましょう！",
            color=discord.Color.blue(),
        )

        # ボタンを作成
        view = UnanimousGameView(self)

        await interaction.response.send_message(embed=embed, view=view)

        # ゲームメッセージを保存
        message = await interaction.original_response()
        self.active_games[guild_id]["message_id"] = message.id

    # ゲームを終了する
    async def end_game(self, guild_id):
        if guild_id in self.active_games:
            self.active_games.pop(guild_id)
            return True
        return False

    # プレイヤーを追加する
    async def add_player(self, guild_id, user):
        if guild_id not in self.active_games:
            return False

        game = self.active_games[guild_id]

        # GMは自動的に参加者とする
        if user.id == game["gm"].id:
            game["participants"][user.id] = user
            return True

        # すでに参加している場合
        if user.id in game["participants"]:
            return False

        # 参加者に追加
        game["participants"][user.id] = user
        return True

    # 回答を受け付ける
    async def submit_answer(self, guild_id, user_id, answer):
        if guild_id not in self.active_games:
            return False, "ゲームが進行中ではありません。"

        game = self.active_games[guild_id]

        if game["status"] != "collecting_answers":
            return False, "現在回答を受け付けていません。"

        if user_id not in game["participants"]:
            return False, "あなたはこのゲームの参加者ではありません。"

        # 回答を記録
        game["answers"][user_id] = answer

        # 全員が回答したかチェック
        if len(game["answers"]) == len(game["participants"]):
            await self.check_answers(guild_id)

        return True, "回答を受け付けました！"

    # 回答をチェックする
    async def check_answers(self, guild_id):
        game = self.active_games[guild_id]
        game["status"] = "completed"

        # 回答を集計
        answers = list(game["answers"].values())
        answer_counts = {}
        for answer in answers:
            answer_lower = answer.lower().strip()
            if answer_lower in answer_counts:
                answer_counts[answer_lower] += 1
            else:
                answer_counts[answer_lower] = 1

        # 最も多い回答を取得
        max_count = max(answer_counts.values())
        most_common = [
            ans for ans, count in answer_counts.items() if count == max_count
        ]

        # 結果を表示するEmbed
        embed = discord.Embed(
            title=f"🎮 全員一致ゲーム - 結果発表",
            description=f"**お題**: {game['topic']}\n",
            color=discord.Color.gold(),
        )

        # 参加者の名前と回答を追加
        for user_id, answer in game["answers"].items():
            user = game["participants"][user_id]
            embed.add_field(name=user.display_name, value=answer, inline=True)

        # 全員一致したかどうか判定
        if len(answer_counts) == 1:
            embed.description += "🎉 全員一致！おめでとうございます！"
            embed.color = discord.Color.green()
            game["consecutive_wins"] += 1
        else:
            embed.description += "😢 残念...全員一致しませんでした。"
            embed.color = discord.Color.red()
            game["consecutive_wins"] = 0

        embed.set_footer(text=f"連続成功回数: {game['consecutive_wins']}")

        # 結果を送信
        channel = game["channel"]
        await channel.send(embed=embed)

        # ゲーム状態をリセット
        self.active_games[guild_id]["status"] = "waiting"
        self.active_games[guild_id]["answers"] = {}


# ゲーム操作用のボタンビュー
class UnanimousGameView(discord.ui.View):
    def __init__(self, game_manager):
        super().__init__(timeout=None)
        self.game_manager = game_manager

    @discord.ui.button(label="参加する", style=discord.ButtonStyle.primary, emoji="✋")
    async def join_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        guild_id = interaction.guild_id
        user = interaction.user

        # プレイヤーを追加
        result = await self.game_manager.add_player(guild_id, user)

        if result:
            await interaction.response.send_message(
                f"ゲームに参加しました！", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "すでに参加しています。", ephemeral=True
            )

    @discord.ui.button(label="回答開始", style=discord.ButtonStyle.success, emoji="▶️")
    async def start_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        guild_id = interaction.guild_id
        user = interaction.user

        # GMのみ開始可能
        if guild_id in self.game_manager.active_games:
            game = self.game_manager.active_games[guild_id]

            if game["gm"].id != user.id:
                await interaction.response.send_message(
                    "GMだけがゲームを開始できます。", ephemeral=True
                )
                return

            if len(game["participants"]) < 2:
                await interaction.response.send_message(
                    "少なくとも2人のプレイヤーが必要です。", ephemeral=True
                )
                return

            game["status"] = "collecting_answers"

            # 参加者にDMを送信
            for participant_id, participant in game["participants"].items():
                try:
                    dm_channel = await participant.create_dm()
                    embed = discord.Embed(
                        title="🎮 全員一致ゲーム - 回答フォーム",
                        description=f"**お題**: {game['topic']}\n\nあなたの回答を入力してください。",
                        color=discord.Color.blue(),
                    )

                    # 回答用のModal
                    await dm_channel.send(
                        embed=embed,
                        view=AnswerView(self.game_manager, guild_id, participant_id),
                    )
                except:
                    await interaction.channel.send(
                        f"{participant.mention} にDMを送信できませんでした。"
                    )

            await interaction.response.send_message(
                "全参加者に回答用DMを送信しました！", ephemeral=True
            )

            # 公開メッセージも更新
            embed = discord.Embed(
                title="🎮 全員一致ゲーム - 回答受付中",
                description=f"**GMは {game['gm'].mention} です**\n\n**お題**: {game['topic']}\n\n参加者はDMで回答を送信してください！",
                color=discord.Color.orange(),
            )

            # 参加者リスト
            participants_text = "\n".join(
                [f"- {p.display_name}" for p in game["participants"].values()]
            )
            embed.add_field(name="参加者", value=participants_text)

            # 回答状況
            embed.add_field(
                name="回答状況", value=f"0 / {len(game['participants'])}", inline=False
            )

            await interaction.message.edit(embed=embed, view=None)
        else:
            await interaction.response.send_message(
                "ゲームが見つかりません。", ephemeral=True
            )

    @discord.ui.button(label="ゲーム終了", style=discord.ButtonStyle.danger, emoji="🛑")
    async def end_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        guild_id = interaction.guild_id
        user = interaction.user

        # GMのみ終了可能
        if guild_id in self.game_manager.active_games:
            game = self.game_manager.active_games[guild_id]

            if game["gm"].id != user.id:
                await interaction.response.send_message(
                    "GMだけがゲームを終了できます。", ephemeral=True
                )
                return

            await self.game_manager.end_game(guild_id)
            await interaction.response.send_message(
                "ゲームを終了しました。", ephemeral=False
            )

            # メッセージを編集
            embed = discord.Embed(
                title="🎮 全員一致ゲーム - 終了",
                description="このゲームは終了しました。",
                color=discord.Color.dark_grey(),
            )
            await interaction.message.edit(embed=embed, view=None)
        else:
            await interaction.response.send_message(
                "ゲームが見つかりません。", ephemeral=True
            )


# 回答用のモーダルビュー
class AnswerModal(discord.ui.Modal, title="回答フォーム"):
    def __init__(self, game_manager, guild_id, user_id):
        super().__init__()
        self.game_manager = game_manager
        self.guild_id = guild_id
        self.user_id = user_id

    answer = discord.ui.TextInput(
        label="あなたの回答",
        placeholder="ここに回答を入力してください",
        min_length=1,
        max_length=100,
    )

    async def on_submit(self, interaction: discord.Interaction):
        success, message = await self.game_manager.submit_answer(
            self.guild_id, self.user_id, self.answer.value
        )

        if success:
            await interaction.response.send_message(
                f"回答を送信しました: **{self.answer.value}**", ephemeral=True
            )

            # 回答状況を更新
            game = self.game_manager.active_games[self.guild_id]
            channel = game["channel"]

            try:
                message = await channel.fetch_message(game["message_id"])
                embed = message.embeds[0]

                # 参加者数と回答数を取得
                total_participants = len(game["participants"])
                answers_received = len(game["answers"])

                # 回答状況フィールドを更新
                for i, field in enumerate(embed.fields):
                    if field.name == "回答状況":
                        embed.set_field_at(
                            i,
                            name="回答状況",
                            value=f"{answers_received} / {total_participants}",
                            inline=False,
                        )
                        break

                await message.edit(embed=embed)
            except:
                # メッセージの更新に失敗しても続行
                pass
        else:
            await interaction.response.send_message(message, ephemeral=True)


# 回答ボタン用のビュー
class AnswerView(discord.ui.View):
    def __init__(self, game_manager, guild_id, user_id):
        super().__init__(timeout=None)
        self.game_manager = game_manager
        self.guild_id = guild_id
        self.user_id = user_id

    @discord.ui.button(label="回答する", style=discord.ButtonStyle.primary, emoji="✏️")
    async def answer_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        # 回答用モーダルを表示
        await interaction.response.send_modal(
            AnswerModal(self.game_manager, self.guild_id, self.user_id)
        )


# コマンド設定関数
def setup_unanimous_game_command(tree):
    game_manager = UnanimousGame()

    # 全員一致ゲームのコマンドグループ
    unanimous_group = app_commands.Group(
        name="全員一致", description="全員一致ゲームに関するコマンド"
    )

    @unanimous_group.command(name="開始", description="全員一致ゲームを開始します")
    @app_commands.describe(お題="ゲームのお題を指定します（省略可能）")
    async def start_game(interaction: discord.Interaction, お題: str = None):
        await game_manager.create_game(interaction, お題)

    @unanimous_group.command(
        name="ヘルプ", description="全員一致ゲームのルールと遊び方を表示します"
    )
    async def game_help(interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎮 全員一致ゲーム - ヘルプ",
            description=game_manager.game_description,
            color=discord.Color.blue(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    tree.add_command(unanimous_group)
