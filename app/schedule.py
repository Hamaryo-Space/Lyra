import discord
import os
from discord import app_commands


# 年間行事コマンドを設定する関数
def setup_schedule_command(tree):
    # 年間行事コマンド
    @tree.command(name="年間行事", description="年間行事予定を表示します")
    @app_commands.choices(
        学期=[
            app_commands.Choice(name="春学期", value="春学期"),
            app_commands.Choice(name="秋学期", value="秋学期"),
        ]
    )
    async def yearly_schedule(interaction: discord.Interaction, 学期: str = None):
        # 現在のスクリプトからの相対パスで画像ファイルの場所を指定
        base_dir = os.path.dirname(os.path.abspath(__file__))
        public_dir = os.path.join(base_dir, "Public")

        # 春学期の画像ファイルパス
        spring_path = os.path.join(public_dir, "春.jpg")
        # 秋学期の画像ファイルパス
        fall_path = os.path.join(public_dir, "秋.jpg")

        try:
            # 引数がない場合は両方の学期の行事を表示
            if 学期 is None:
                # 春学期の画像を送信
                spring_file = discord.File(spring_path, filename="春.jpg")
                # 秋学期の画像を送信
                fall_file = discord.File(fall_path, filename="秋.jpg")

                await interaction.response.send_message(
                    "**2025年度 文教大学行事予定**",
                    files=[spring_file, fall_file],
                    silent=True,
                )

            # 春学期のみ表示
            elif 学期 == "春学期":
                spring_file = discord.File(spring_path, filename="春.jpg")
                await interaction.response.send_message(
                    "**2025年度 文教大学行事予定 (春学期)**",
                    files=[spring_file],
                    silent=True,
                )

            # 秋学期のみ表示
            elif 学期 == "秋学期":
                fall_file = discord.File(fall_path, filename="秋.jpg")
                await interaction.response.send_message(
                    "**2025年度 文教大学行事予定 (秋学期)**",
                    files=[fall_file],
                    silent=True,
                )

        except FileNotFoundError as e:
            await interaction.response.send_message(
                f"ファイルが見つかりませんでした: {str(e)}", ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"エラーが発生しました: {str(e)}", ephemeral=True
            )
