import discord
from discord import app_commands
import datetime
from collections import Counter
import matplotlib.pyplot as plt
import io
import os


class ServerStats:
    def __init__(self):
        self.stats_description = """
**【サーバー統計】**
このコマンドではDiscordサーバーの様々な統計情報を確認できます。
メンバー数、ロール分布、チャンネル数など、サーバーの現状を分析できます。
"""

    async def get_member_stats(self, guild):
        """メンバーに関する統計を取得します"""
        total_members = guild.member_count
        humans = len([m for m in guild.members if not m.bot])
        bots = len([m for m in guild.members if m.bot])
        online = len([m for m in guild.members if m.status == discord.Status.online])
        offline = len([m for m in guild.members if m.status == discord.Status.offline])

        # ステータス別にカウント
        status_counts = {
            "オンライン": len(
                [m for m in guild.members if m.status == discord.Status.online]
            ),
            "退席中": len(
                [m for m in guild.members if m.status == discord.Status.idle]
            ),
            "取り込み中": len(
                [m for m in guild.members if m.status == discord.Status.dnd]
            ),
            "オフライン": len(
                [m for m in guild.members if m.status == discord.Status.offline]
            ),
        }

        # モバイルユーザー数
        mobile_users = sum(
            1 for m in guild.members if hasattr(m, "is_on_mobile") and m.is_on_mobile()
        )

        return {
            "total": total_members,
            "humans": humans,
            "bots": bots,
            "online": online,
            "offline": offline,
            "status_counts": status_counts,
            "mobile_users": mobile_users,
        }

    async def get_role_stats(self, guild):
        """ロールに関する統計を取得します"""
        roles = guild.roles
        role_counts = {}

        # 各ロールに所属するメンバー数をカウント
        for role in roles:
            if not role.is_default():  # @everyoneを除く
                role_counts[role.name] = len(role.members)

        return {
            "total_roles": len(roles) - 1,  # @everyoneを除く
            "role_counts": role_counts,
        }

    async def get_channel_stats(self, guild):
        """チャンネルに関する統計を取得します"""
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)

        return {
            "text_channels": text_channels,
            "voice_channels": voice_channels,
            "categories": categories,
            "total_channels": text_channels + voice_channels,
        }

    async def get_activity_stats(self, guild):
        """メンバーのアクティビティに関する統計を取得します"""
        activities = []

        for member in guild.members:
            for activity in member.activities:
                if activity.type == discord.ActivityType.playing:
                    activities.append(activity.name)

        # 最も人気のあるゲーム/アクティビティ
        activity_counter = Counter(activities)
        popular_activities = activity_counter.most_common(5)

        return {
            "playing_count": len(activities),
            "popular_activities": popular_activities,
        }

    async def create_member_chart(self, stats):
        """メンバー統計のグラフを作成します"""
        # グラフサイズ設定
        plt.figure(figsize=(10, 6))

        # 日本語フォントの設定
        plt.rcParams["font.family"] = "sans-serif"
        plt.rcParams["font.sans-serif"] = [
            "Arial",
            "Yu Gothic",
            "Meiryo",
            "Hiragino Kaku Gothic ProN",
        ]

        # 人間とボットの割合の円グラフ
        plt.subplot(1, 2, 1)
        labels = ["人間", "ボット"]
        sizes = [stats["humans"], stats["bots"]]
        colors = ["#3498db", "#e74c3c"]
        plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
        plt.title("メンバー構成")

        # ステータス別の棒グラフ
        plt.subplot(1, 2, 2)
        status_labels = list(stats["status_counts"].keys())
        status_values = list(stats["status_counts"].values())
        colors = ["#2ecc71", "#f1c40f", "#e74c3c", "#95a5a6"]
        plt.bar(status_labels, status_values, color=colors)
        plt.title("メンバーステータス")
        plt.xticks(rotation=45, ha="right")

        plt.tight_layout()

        # 画像をバイトストリームとして保存
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        plt.close()

        return buffer

    async def create_server_summary(self, interaction, option):
        """サーバーの統計情報を生成します"""
        guild = interaction.guild
        created_at = guild.created_at.strftime("%Y年%m月%d日")

        # タイムゾーンを統一してから計算（Discordのタイムスタンプはawareなので、nowもawareにする）
        now = datetime.datetime.now(datetime.timezone.utc)
        server_age = (now - guild.created_at).days

        # サーバー情報を取得
        member_stats = await self.get_member_stats(guild)
        role_stats = await self.get_role_stats(guild)
        channel_stats = await self.get_channel_stats(guild)

        # サーバーアイコンのURL
        server_icon = guild.icon.url if guild.icon else None

        # Embedを作成
        embed = discord.Embed(
            title=f"📊 {guild.name} - サーバー統計",
            description=f"サーバー作成日: {created_at} ({server_age}日前)",
            color=discord.Color.blue(),
        )

        if server_icon:
            embed.set_thumbnail(url=server_icon)

        # メンバー情報
        embed.add_field(
            name="👥 メンバー情報",
            value=f"総メンバー数: {member_stats['total']}\n"
            f"人間: {member_stats['humans']}\n"
            f"ボット: {member_stats['bots']}\n"
            f"オンライン: {member_stats['online']}\n"
            f"モバイルユーザー: {member_stats['mobile_users']}",
            inline=True,
        )

        # チャンネル情報
        embed.add_field(
            name="📝 チャンネル情報",
            value=f"テキストチャンネル: {channel_stats['text_channels']}\n"
            f"ボイスチャンネル: {channel_stats['voice_channels']}\n"
            f"カテゴリー: {channel_stats['categories']}\n"
            f"合計: {channel_stats['total_channels']}",
            inline=True,
        )

        # ロール情報
        top_roles = sorted(
            role_stats["role_counts"].items(), key=lambda x: x[1], reverse=True
        )[:5]
        top_roles_text = (
            "\n".join([f"{role}: {count}人" for role, count in top_roles])
            if top_roles
            else "なし"
        )

        embed.add_field(
            name=f"🏷️ ロール情報 (総数: {role_stats['total_roles']})",
            value=f"**上位5ロール**\n{top_roles_text}",
            inline=False,
        )

        # アクティビティ情報をエラーハンドリング付きで取得
        try:
            activity_stats = await self.get_activity_stats(guild)
            activities_text = (
                "\n".join(
                    [
                        f"{activity}: {count}人"
                        for activity, count in activity_stats["popular_activities"]
                    ]
                )
                if activity_stats["popular_activities"]
                else "なし"
            )

            embed.add_field(
                name="🎮 人気のアクティビティ",
                value=activities_text or "アクティブなユーザーがいません",
                inline=False,
            )
        except Exception as e:
            embed.add_field(
                name="🎮 人気のアクティビティ",
                value="アクティビティ情報の取得に失敗しました",
                inline=False,
            )

        # サーバーのブーストレベルと数
        if guild.premium_tier > 0:
            embed.add_field(
                name="🚀 サーバーブースト",
                value=f"レベル: {guild.premium_tier}\nブースト数: {guild.premium_subscription_count}",
                inline=True,
            )

        # グラフを作成するかどうか
        if option in ["グラフ", "完全"]:
            try:
                chart = await self.create_member_chart(member_stats)
                file = discord.File(chart, filename="member_stats.png")
                embed.set_image(url="attachment://member_stats.png")

                await interaction.response.send_message(embed=embed, file=file)
            except Exception as e:
                embed.add_field(
                    name="エラー",
                    value=f"グラフの生成に失敗しました: {str(e)}",
                    inline=False,
                )
                await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(embed=embed)


# コマンド設定関数
def setup_server_stats_command(tree):
    stats_instance = ServerStats()  # ここでインスタンス作成

    # サーバー統計コマンドグループ
    stats_group = app_commands.Group(
        name="サーバー", description="サーバーの統計情報を表示するコマンド"
    )

    @stats_group.command(name="統計", description="サーバーの統計情報を表示します")
    @app_commands.choices(
        表示オプション=[
            app_commands.Choice(name="基本情報", value="基本"),
            app_commands.Choice(name="グラフ付き", value="グラフ"),
            app_commands.Choice(name="完全な統計", value="完全"),
        ]
    )
    async def server_stats(
        interaction: discord.Interaction, 表示オプション: str = "基本"
    ):
        """サーバーの統計情報を表示します"""
        await stats_instance.create_server_summary(
            interaction, 表示オプション
        )  # インスタンスを使用

    @stats_group.command(
        name="ユーザー", description="特定のユーザーの情報を表示します"
    )
    @app_commands.describe(メンバー="情報を表示したいメンバー")
    async def user_info(
        interaction: discord.Interaction, メンバー: discord.Member = None
    ):
        """ユーザー情報を表示します"""
        # ユーザーが指定されていない場合はコマンド実行者の情報を表示
        user = メンバー or interaction.user

        # ユーザー作成日とサーバー参加日
        created_at = user.created_at.strftime("%Y年%m月%d日 %H:%M")
        joined_at = (
            user.joined_at.strftime("%Y年%m月%d日 %H:%M") if user.joined_at else "不明"
        )

        # タイムゾーンを統一してから計算
        now = datetime.datetime.now(datetime.timezone.utc)
        account_age = (now - user.created_at).days
        server_age = (now - user.joined_at).days if user.joined_at else 0

        # ステータスとカスタムステータス
        status_emojis = {
            discord.Status.online: "🟢",
            discord.Status.idle: "🟡",
            discord.Status.dnd: "🔴",
            discord.Status.offline: "⚫",
        }

        # ステータスを安全に取得
        try:
            status_emoji = status_emojis.get(user.status, "⚫")
            status_text = str(user.status).title()
        except:
            status_emoji = "⚫"
            status_text = "不明"

        # カスタムステータスを安全に取得
        custom_status = "なし"
        try:
            for activity in user.activities:
                if isinstance(activity, discord.CustomActivity) and activity.name:
                    custom_status = activity.name
                    break
        except:
            pass

        # Embedを作成
        embed = discord.Embed(
            title=f"{user.name}の情報",
            description=f"ID: {user.id}",
            color=(
                user.color
                if user.color != discord.Color.default()
                else discord.Color.blue()
            ),
        )

        embed.set_thumbnail(url=user.display_avatar.url)

        # 基本情報
        embed.add_field(
            name="📝 基本情報",
            value=f"**ニックネーム:** {user.display_name}\n"
            f"**ステータス:** {status_emoji} {status_text}\n"
            f"**カスタムステータス:** {custom_status}\n"
            f"**ボット:** {'はい' if user.bot else 'いいえ'}\n",
            inline=False,
        )

        # タイムライン情報
        embed.add_field(
            name="📅 タイムライン",
            value=f"**アカウント作成:** {created_at} ({account_age}日前)\n"
            f"**サーバー参加:** {joined_at} ({server_age}日前)",
            inline=False,
        )

        # ロール情報
        roles = [role.mention for role in user.roles if not role.is_default()]
        roles_text = ", ".join(roles) if roles else "なし"

        embed.add_field(
            name=f"🏷️ ロール ({len(roles)})",
            value=(
                roles_text
                if len(roles_text) < 1024
                else f"{len(roles)}個のロールがあります"
            ),
            inline=False,
        )

        # アクティビティ情報を安全に取得
        try:
            activities = []
            for activity in user.activities:
                if isinstance(activity, discord.Game):
                    activities.append(f"🎮 プレイ中: {activity.name}")
                elif isinstance(activity, discord.Streaming):
                    activities.append(
                        f"📹 配信中: {activity.name} ({activity.platform})"
                    )
                elif isinstance(activity, discord.Spotify):
                    activities.append(
                        f"🎵 Spotify: {activity.title} by {activity.artist}"
                    )

            if activities:
                embed.add_field(
                    name="🎯 アクティビティ", value="\n".join(activities), inline=False
                )
        except:
            pass

        # バッジ情報を安全に取得
        try:
            badge_mapping = {
                discord.UserFlags.staff: "👨‍💼 Discord スタッフ",
                discord.UserFlags.partner: "🤝 Discord パートナー",
                discord.UserFlags.hypesquad: "🏠 HypeSquad イベント",
                discord.UserFlags.bug_hunter: "🐛 バグハンター",
                discord.UserFlags.hypesquad_bravery: "🔴 HypeSquad Bravery",
                discord.UserFlags.hypesquad_brilliance: "🟣 HypeSquad Brilliance",
                discord.UserFlags.hypesquad_balance: "🟢 HypeSquad Balance",
                discord.UserFlags.early_supporter: "👑 アーリーサポーター",
                discord.UserFlags.team_user: "👥 Team User",
                discord.UserFlags.bug_hunter_level_2: "🐛 バグハンター レベル2",
                discord.UserFlags.verified_bot: "✅ 認証済みボット",
                discord.UserFlags.verified_bot_developer: "🧑‍💻 認証済みボット開発者",
                discord.UserFlags.discord_certified_moderator: "🛡️ 認証済みモデレーター",
                discord.UserFlags.active_developer: "👨‍💻 アクティブ開発者",
            }

            badges = []
            for flag, badge_text in badge_mapping.items():
                if user.public_flags.value & flag.value:
                    badges.append(badge_text)

            if badges:
                embed.add_field(name="🏅 バッジ", value="\n".join(badges), inline=False)
        except:
            pass

        await interaction.response.send_message(embed=embed)

    tree.add_command(stats_group)
