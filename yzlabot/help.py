import discord
from discord.ext import commands

# TODO: i18nに対応させる


class YLHelpCommand(commands.DefaultHelpCommand):
    def __init__(self, **options):
        super().__init__(**options)
        self.commands_heading = "コマンド:"
        self.no_category = "その他"
        self.command_attrs["help"] = "YZ-LABOで使用できるコマンド一覧を表示します。"

    def get_ending_note(self):
        return (
            "※使用できるコマンドのみ表示されています。\n"
            "各コマンドやカテゴリの詳しい説明を見たい場合はhelpコマンドの後にコマンド名や"
            "カテゴリ名を入力して下さい。"
        )

    def command_not_found(self, string):
        return f"{string} はYZ-LABOTのコマンドには存在しません。"

    def subcommand_not_found(self, command, string):
        if isinstance(command, commands.Group) and \
                len(command.all_commands) > 0:
            return f"{command.qualified_name} に {string} というサブコマンドは登録されていません。"
        return f"{command.qualified_name} にサブコマンドは登録されていません。"

    async def send_bot_help(self, mapping):
        content = ""
        for cog in mapping:
            # 各コグのコマンド一覧を content に追加していく
            command_list = await self.filter_commands(mapping[cog])
            if not command_list:
                # 表示できるコマンドがないので、他のコグの処理に移る
                continue
            if cog is None:
                # コグが未設定のコマンドなので、no_category属性を参照する
                content += f"```\n{self.no_category}```"
            else:
                content += \
                    f"```\n{cog.qualified_name} / {cog.description}\n```"
            for command in command_list:
                if command.name == "help":
                    content += f"`{command.name}` / {command.help}\n"
                else:
                    content += f"`{command.name}` / {command.brief}\n"
            content += "\n"

        embed = discord.Embed(
            title="YZ-LABOT コマンド一覧",
            description=content,
            color=discord.Colour.green()
        )

        embed.add_field(
            name="Note",
            value=self.get_ending_note(),
            inline=False
        )

        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        color = discord.Colour.green()
        content = ""
        command_list = await self.filter_commands(cog.get_commands())
        content += f"```\n{cog.qualified_name} / {cog.description}\n```"
        for command in command_list:
            content += f"`{command.name}` / {command.brief}\n"
        content += "\n"
        if not content:
            content = "表示できるコマンドがありません。"
            color = discord.Colour.red()

        embed = discord.Embed(
            title="YZ-LABOT コマンド一覧",
            description=content,
            color=color
        )

        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        embed = discord.Embed(
            title=self.get_command_signature(group),
            description=group.description,
            color=discord.Colour.green()
        )
        if group.help:
            embed.add_field(
                name="説明:",
                value=group.help,
                inline=False
            )
        content = ""
        command_list = await self.filter_commands(group.commands)
        for command in command_list:
            content += f"`{command.name}` / {command.description}\n"
        if content == "":
            content = "(サブコマンドが定義されていません。)"
        embed.add_field(
            name="サブコマンド一覧",
            value=content,
            inline=False
        )

        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(
            title=self.get_command_signature(command),
            description=command.description,
            color=discord.Colour.green()
        )
        if command.help:
            embed.add_field(
                name="説明:",
                value=command.help,
                inline=False
            )

        await self.get_destination().send(embed=embed)

    async def send_error_message(self, error):
        embed = discord.Embed(
            title="ヘルプエラー",
            description=error,
            color=discord.Colour.red()
        )
        await self.get_destination().send(embed=embed)
