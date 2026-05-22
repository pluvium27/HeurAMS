"""命令行入口
"""

import platform
import click
from heurams.i18n import _, setup_locale
from heurams.services.version import ver, stage, codename, codename_cn
from heurams.services.logger import get_logger

logger = get_logger(__name__)

def _apply_locale(ctx, param, value):
    """立即显式应用 locale"""
    if value:
        setup_locale(value)
    return value


class _I18nGroup(click.Group):
    """在运行时完成翻译工作的命令组"""

    _option_help_map: dict[str, str] = {
        "version": "Show the version and exit.",
        "locale": "Explicitly specify locale (defaults to LANG env).",
        "host": "Listening address",
        "port": "Listening port",
        "reload": "Development mode hot reload",
    }

    def format_help(self, ctx, formatter):
        # 重新翻译每个子命令的帮助信息
        for cmd in self.commands.values():
            raw = getattr(cmd, "_raw_help", None)
            if raw is not None:
                cmd.help = _(raw)
        # Re-translate every option's help text by name lookup.
        for param in self.params:
            if isinstance(param, click.Option) and param.name in self._option_help_map:
                param.help = _(self._option_help_map[param.name])
        self.help = _("HeurAMS {ver} - Heuristic Auxiliary Memorizing Scheduler").format(
            ver=ver
        )
        return super().format_help(ctx, formatter)


class _I18nCommand(click.Command):
    """在运行时完成翻译工作的命令"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._raw_help = self.help or (self.short_help or "")


@click.group(
    cls=_I18nGroup,
    invoke_without_command=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.version_option(
    ver, "-v", "--version",
    prog_name="HeurAMS",
    message=f"%(prog)s %(version)s {stage} ({codename}/{codename_cn}), {platform.system()}",
    help=_I18nGroup._option_help_map["version"],
)
@click.option(
    "--locale", "-l", default=None,
    callback=_apply_locale,
    is_eager=True,
    expose_value=True,
    help=_I18nGroup._option_help_map["locale"],
)
@click.pass_context
def cli(ctx, locale):
    if ctx.invoked_subcommand is None:
        click.echo(cli.get_help(ctx))
        ctx.exit(0)


@cli.command(cls=_I18nCommand)
def tui():
    """Launch the built-in user interface (TUI)"""
    import heurams.interface.__main__ as tui_module

    tui_module.main()


@cli.command(cls=_I18nCommand)
@click.option("--host", default="127.0.0.1", help=_I18nGroup._option_help_map["host"])
@click.option("--port", default=8821, help=_I18nGroup._option_help_map["port"], type=int)
@click.option("--reload", is_flag=True, help=_I18nGroup._option_help_map["reload"])
def serve(host, port, reload):
    """Launch the API service (unifront)"""
    from heurams.unifront.server import create_app

    app = create_app()
    click.echo(
        _("unifront API service started: http://{host}:{port}").format(
            host=host, port=port
        )
    )
    import uvicorn

    uvicorn.run(app, host=host, port=port, reload=reload, log_level="info")


@cli.command(cls=_I18nCommand, name="help")
@click.pass_context
def help_cmd(ctx):
    """Show this help message"""
    click.echo(cli.get_help(ctx.parent))


def main():
    cli()

if __name__ == "__main__":
    logger.info("HeurAMS cmdline entrypoint invoked")
    main()