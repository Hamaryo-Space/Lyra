import json
import discord
import os
from discord import app_commands
from datetime import datetime


# 設定ファイルを読み込む関数
def load_config():
    try:
        # 絶対パスで指定
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, "config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # デフォルト設定を返す
        return {"use_embed": True, "default_color": "#3498db"}


# 次のゼミ情報を取得する関数
def get_next_seminar():
    try:
        # 絶対パスで指定
        base_dir = os.path.dirname(os.path.abspath(__file__))
        schedule_path = os.path.join(base_dir, "Public", "ゼミ日程.json")
        with open(schedule_path, "r", encoding="utf-8") as f:
            schedules = json.load(f)

        # 現在の日時を取得
        current_date = datetime.now().strftime("%Y-%m-%d")

        # 次回の日程を探す
        for schedule in schedules:
            if schedule["date"] >= current_date:
                return schedule
        return None
    except Exception as e:
        print(f"ゼミ日程の取得エラー: {str(e)}")
        return None


# ゼミ日程コマンドを設定する関数
def setup_seminar_command(tree):
    @tree.command(name="ゼミ日程", description="ゼミの日程を表示します")
    @app_commands.choices(
        オプション=[
            app_commands.Choice(name="次回", value="次回"),
            app_commands.Choice(name="json", value="json"),
        ]
    )
    async def seminar_schedule(
        interaction: discord.Interaction, オプション: str = None
    ):
        try:
            # 設定を読み込む
            config = load_config()
            use_embed = config.get("use_embed", True)
            embed_color = int(
                config.get("default_color", "#3498db").replace("#", "0x"), 16
            )

            # JSONファイルからゼミ日程を絶対パスで読み込み
            base_dir = os.path.dirname(os.path.abspath(__file__))
            schedule_path = os.path.join(base_dir, "Public", "ゼミ日程.json")
            with open(schedule_path, "r", encoding="utf-8") as f:
                schedules = json.load(f)

            # 現在の日時を取得
            current_date = datetime.now().strftime("%Y-%m-%d")

            # オプションに応じた処理
            if オプション == "json":
                # JSONをそのまま返す
                json_str = json.dumps(schedules, ensure_ascii=False, indent=2)
                await interaction.response.send_message(
                    f"```json\n{json_str}\n```", silent=True
                )
                return

            elif オプション == "次回":
                # 次回の日程だけを返す
                next_schedule = None
                for schedule in schedules:
                    if schedule["date"] >= current_date:
                        next_schedule = schedule
                        break

                if next_schedule:
                    if use_embed:
                        # Discord標準のEmbedを使用して次回の日程を表示
                        embed = discord.Embed(
                            title="次回のゼミ日程",
                            description="",
                            color=embed_color,
                        )
                        embed.add_field(
                            name="日付",
                            value=format_date(next_schedule["date"]),
                            inline=True,
                        )
                        embed.add_field(
                            name="時間", value=next_schedule["time"], inline=True
                        )
                        embed.add_field(
                            name="科目", value=next_schedule["subject"], inline=True
                        )
                        embed.add_field(
                            name="週目", value=next_schedule["number"], inline=False
                        )
                        await interaction.response.send_message(
                            embed=embed, silent=True
                        )
                    else:
                        # テキストベースでのメッセージを送信
                        response = f"**次回のゼミ日程**\n"
                        response += f"📅 日付: {format_date(next_schedule['date'])}\n"
                        response += f"⏰ 時間: {next_schedule['time']}\n"
                        # response += f"📚 科目: {next_schedule['subject']}\n"
                        response += f"🔢 週回数: {next_schedule['number']}"
                        await interaction.response.send_message(response, silent=True)
                else:
                    await interaction.response.send_message(
                        "次回のゼミ日程はありません。", silent=True
                    )
                return

            else:
                # 全ての日程を表示
                embed = discord.Embed(
                    title="ゼミ日程一覧",
                    description="卒業研究Ⅰのゼミ日程です",
                    color=discord.Color.green(),
                )

                upcoming_schedules = []
                past_schedules = []

                for schedule in schedules:
                    # 日付でソートして現在より前か後かを判断
                    if schedule["date"] >= current_date:
                        upcoming_schedules.append(schedule)
                    else:
                        past_schedules.append(schedule)

                # 未来の予定を表示
                if upcoming_schedules:
                    embed.add_field(
                        name="【今後の予定】",
                        value="\n".join(
                            [
                                f"・{format_date(s['date'])} {s['time']} {s['number']}"
                                for s in upcoming_schedules
                            ]
                        ),
                        inline=False,
                    )
                else:
                    embed.add_field(
                        name="【今後の予定】", value="予定はありません", inline=False
                    )

                # 過去の予定を表示
                if past_schedules:
                    embed.add_field(
                        name="【過去の予定】",
                        value="\n".join(
                            [
                                f"・{format_date(s['date'])} {s['time']} {s['number']}"
                                for s in past_schedules
                            ]
                        ),
                        inline=False,
                    )

                await interaction.response.send_message(embed=embed, silent=True)

        except Exception as e:
            await interaction.response.send_message(
                f"エラーが発生しました: {str(e)}", silent=True
            )


# 日付のフォーマットを整える関数（YYYY-MM-DD → YYYY年MM月DD日）
def format_date(date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.strftime("%Y年%m月%d日")
